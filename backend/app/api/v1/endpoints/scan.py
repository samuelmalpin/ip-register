from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.ip_address import IPAddress, IPStatus
from app.models.subnet import Subnet
from app.models.user import User, UserRole
from app.services.scan_service import apply_dhcp_range_status, map_scan_result, resolve_mac_addresses, run_nmap_scan
from app.utils.audit import add_audit_log


router = APIRouter(prefix="/scan", tags=["scan"])


@router.post("/{subnet_id}")
async def scan_subnet(
    subnet_id: int,
    admin: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    subnet = await db.get(Subnet, subnet_id)
    if not subnet:
        raise HTTPException(status_code=404, detail="Subnet not found")

    existing_result = await db.execute(select(IPAddress).where(IPAddress.subnet_id == subnet_id))
    existing_rows = existing_result.scalars().all()
    existing_by_address = {row.address: row for row in existing_rows}
    existing_ips = set(existing_by_address.keys())

    try:
        scanned_ips = await run_nmap_scan(subnet.cidr)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    mapped = map_scan_result(existing_ips, scanned_ips)
    mapped = apply_dhcp_range_status(mapped, subnet.dhcp_start, subnet.dhcp_end)
    mac_map = resolve_mac_addresses(scanned_ips)

    for row in mapped:
        row["mac_address"] = mac_map.get(row["address"])

    created = 0
    updated = 0
    for row in mapped:
        address = row["address"]
        status = IPStatus(row["status"])
        mac_address = row.get("mac_address")
        if address in existing_by_address:
            ip_row = existing_by_address[address]
            if ip_row.status != status:
                ip_row.status = status
                updated += 1
            if mac_address and ip_row.mac_address != mac_address:
                ip_row.mac_address = mac_address
                updated += 1
            continue

        db.add(
            IPAddress(
                address=address,
                status=status,
                mac_address=mac_address,
                site_id=subnet.site_id,
                subnet_id=subnet.id,
            )
        )
        created += 1

    await db.commit()
    await add_audit_log(db, admin.id, "SCAN", "Subnet", subnet_id)
    return {
        "subnet": subnet.cidr,
        "results": mapped,
        "persisted": {
            "created": created,
            "updated": updated,
            "total_detected": len(mapped),
        },
    }
