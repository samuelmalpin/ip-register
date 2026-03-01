from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
import ipaddress
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.ip_address import IPAddress
from app.models.user import User, UserRole
from app.schemas.ip_address import IPAddressCreate, IPAddressResponse, IPAddressUpdate
from app.services.csv_service import export_ips_to_csv, import_ips_from_csv
from app.services.ip_service import suggest_free_ip
from app.utils.audit import add_audit_log
from app.utils.sanitize import sanitize_text
import io


router = APIRouter(prefix="/ips", tags=["ips"])


@router.get("", response_model=list[IPAddressResponse])
async def list_ips(_: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IPAddress))
    rows = result.scalars().all()
    def sort_key(row: IPAddress):
        try:
            return (0, int(ipaddress.ip_address(row.address)))
        except ValueError:
            return (1, row.address)

    return sorted(rows, key=sort_key)


@router.post("", response_model=IPAddressResponse, status_code=status.HTTP_201_CREATED)
async def create_ip(
    payload: IPAddressCreate,
    user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    ip = IPAddress(
        address=payload.address,
        status=payload.status,
        hostname=sanitize_text(payload.hostname, 255),
        mac_address=sanitize_text(payload.mac_address, 64),
        site_id=payload.site_id,
        subnet_id=payload.subnet_id,
    )
    db.add(ip)
    await db.commit()
    await db.refresh(ip)
    await add_audit_log(db, user.id, "CREATE", "IPAddress", ip.id)
    return ip


@router.patch("/{ip_id}", response_model=IPAddressResponse)
async def update_ip(
    ip_id: int,
    payload: IPAddressUpdate,
    user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    ip = await db.get(IPAddress, ip_id)
    if not ip:
        raise HTTPException(status_code=404, detail="IP not found")

    if payload.status is not None:
        ip.status = payload.status
    if payload.hostname is not None:
        ip.hostname = sanitize_text(payload.hostname, 255)
    if payload.mac_address is not None:
        ip.mac_address = sanitize_text(payload.mac_address, 64)

    await db.commit()
    await db.refresh(ip)
    await add_audit_log(db, user.id, "UPDATE", "IPAddress", ip.id)
    return ip


@router.delete("/{ip_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ip(
    ip_id: int,
    user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    ip = await db.get(IPAddress, ip_id)
    if not ip:
        raise HTTPException(status_code=404, detail="IP not found")

    await db.delete(ip)
    await db.commit()
    await add_audit_log(db, user.id, "DELETE", "IPAddress", ip_id)
    return None


@router.get("/suggest/{subnet_id}")
async def suggest_ip(
    subnet_id: int,
    gateway_ip: str | None = None,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        return {"suggested_ip": await suggest_free_ip(db, subnet_id, gateway_ip)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/import", dependencies=[Depends(require_role(UserRole.ADMIN))])
async def import_csv(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    if file.content_type not in {"text/csv", "application/vnd.ms-excel"}:
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    try:
        result = await import_ips_from_csv(db, file)
        await add_audit_log(db, user.id, "IMPORT", "IPAddress", None)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/export")
async def export_csv(_: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IPAddress))
    rows = [
        {
            "id": row.id,
            "address": row.address,
            "status": row.status.value,
            "hostname": row.hostname or "",
            "mac_address": row.mac_address or "",
            "site_id": row.site_id,
            "subnet_id": row.subnet_id,
        }
        for row in result.scalars().all()
    ]
    csv_data = export_ips_to_csv(rows)
    stream = io.BytesIO(csv_data.encode("utf-8"))
    headers = {"Content-Disposition": "attachment; filename=ip_export.csv"}
    return StreamingResponse(stream, media_type="text/csv", headers=headers)
