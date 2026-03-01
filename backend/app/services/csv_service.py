import csv
import io
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import get_settings
from app.models.ip_address import IPAddress, IPStatus
from app.utils.sanitize import sanitize_text


REQUIRED_COLUMNS = {"address", "status", "hostname", "mac_address", "site_id", "subnet_id"}


async def import_ips_from_csv(db: AsyncSession, file: UploadFile) -> dict:
    settings = get_settings()
    content = await file.read()

    if len(content) > settings.csv_max_size_bytes:
        raise ValueError("CSV file too large")

    decoded = content.decode("utf-8", errors="strict")
    reader = csv.DictReader(io.StringIO(decoded))

    if not reader.fieldnames or set(reader.fieldnames) != REQUIRED_COLUMNS:
        raise ValueError("Invalid CSV schema")

    created = 0
    errors = []

    try:
        for index, row in enumerate(reader, start=2):
            try:
                ip = IPAddress(
                    address=sanitize_text(row["address"], 64),
                    status=IPStatus[row["status"]],
                    hostname=sanitize_text(row.get("hostname"), 255),
                    mac_address=sanitize_text(row.get("mac_address"), 64),
                    site_id=int(row["site_id"]),
                    subnet_id=int(row["subnet_id"]),
                )
                db.add(ip)
                created += 1
            except Exception as exc:
                errors.append({"line": index, "error": str(exc)})

        if errors:
            await db.rollback()
            return {"created": 0, "errors": errors}

        await db.commit()
        return {"created": created, "errors": []}
    except Exception:
        await db.rollback()
        raise


def export_ips_to_csv(rows: list[dict]) -> str:
    output = io.StringIO()
    fieldnames = ["id", "address", "status", "hostname", "mac_address", "site_id", "subnet_id"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()
