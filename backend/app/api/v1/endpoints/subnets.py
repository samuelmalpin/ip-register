from fastapi import APIRouter, Depends, HTTPException, status
import ipaddress
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.site import Site
from app.models.subnet import Subnet
from app.models.user import User, UserRole
from app.schemas.subnet import SubnetCreate, SubnetResponse, SubnetUpdate
from app.utils.audit import add_audit_log


router = APIRouter(prefix="/subnets", tags=["subnets"])


def validate_dhcp_range(cidr: str, dhcp_start: str | None, dhcp_end: str | None) -> None:
    if (dhcp_start is None) != (dhcp_end is None):
        raise HTTPException(status_code=400, detail="dhcp_start and dhcp_end must be provided together")
    if dhcp_start is None or dhcp_end is None:
        return

    network = ipaddress.ip_network(cidr, strict=False)
    start_ip = ipaddress.ip_address(dhcp_start)
    end_ip = ipaddress.ip_address(dhcp_end)

    if start_ip not in network or end_ip not in network:
        raise HTTPException(status_code=400, detail="DHCP range must be inside subnet CIDR")
    if int(start_ip) > int(end_ip):
        raise HTTPException(status_code=400, detail="dhcp_start must be lower than or equal to dhcp_end")


@router.get("", response_model=list[SubnetResponse])
async def list_subnets(_: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Subnet).order_by(Subnet.id.desc()))
    return result.scalars().all()


@router.post("", response_model=SubnetResponse, status_code=status.HTTP_201_CREATED)
async def create_subnet(
    payload: SubnetCreate,
    user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    site = await db.get(Site, payload.site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    validate_dhcp_range(payload.cidr, payload.dhcp_start, payload.dhcp_end)

    subnet = Subnet(
        cidr=payload.cidr,
        site_id=payload.site_id,
        dhcp_start=payload.dhcp_start,
        dhcp_end=payload.dhcp_end,
    )
    db.add(subnet)
    await db.commit()
    await db.refresh(subnet)
    await add_audit_log(db, user.id, "CREATE", "Subnet", subnet.id)
    return subnet


@router.patch("/{subnet_id}", response_model=SubnetResponse)
async def update_subnet(
    subnet_id: int,
    payload: SubnetUpdate,
    user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    subnet = await db.get(Subnet, subnet_id)
    if not subnet:
        raise HTTPException(status_code=404, detail="Subnet not found")

    if payload.cidr is not None:
        subnet.cidr = payload.cidr
    if payload.dhcp_start is not None or payload.dhcp_end is not None:
        next_start = payload.dhcp_start if payload.dhcp_start is not None else subnet.dhcp_start
        next_end = payload.dhcp_end if payload.dhcp_end is not None else subnet.dhcp_end
        validate_dhcp_range(subnet.cidr, next_start, next_end)
        subnet.dhcp_start = next_start
        subnet.dhcp_end = next_end

    await db.commit()
    await db.refresh(subnet)
    await add_audit_log(db, user.id, "UPDATE", "Subnet", subnet.id)
    return subnet


@router.delete("/{subnet_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subnet(
    subnet_id: int,
    user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    subnet = await db.get(Subnet, subnet_id)
    if not subnet:
        raise HTTPException(status_code=404, detail="Subnet not found")

    await db.delete(subnet)
    await db.commit()
    await add_audit_log(db, user.id, "DELETE", "Subnet", subnet_id)
    return None
