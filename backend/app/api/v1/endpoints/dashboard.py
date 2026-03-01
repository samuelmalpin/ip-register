from collections import defaultdict
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.ip_address import IPAddress, IPStatus
from app.models.site import Site
from app.models.subnet import Subnet
from app.models.user import User
from app.schemas.dashboard import DashboardStats


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def dashboard_stats(_: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    ip_result = await db.execute(select(IPAddress))
    ips = ip_result.scalars().all()

    site_result = await db.execute(select(Site))
    site_map = {site.id: site.name for site in site_result.scalars().all()}

    subnet_result = await db.execute(select(Subnet))
    subnet_map = {subnet.id: subnet.cidr for subnet in subnet_result.scalars().all()}

    total = len(ips)
    used = sum(1 for ip in ips if ip.status != IPStatus.FREE)
    free = total - used

    by_site: dict[str, int] = defaultdict(int)
    by_subnet: dict[str, int] = defaultdict(int)

    for ip in ips:
        by_site[site_map.get(ip.site_id, "unknown")] += 1
        by_subnet[subnet_map.get(ip.subnet_id, "unknown")] += 1

    return DashboardStats(
        total_ips=total,
        used_ips=used,
        free_ips=free,
        free_percentage=(free / total * 100) if total else 100.0,
        by_site=dict(by_site),
        by_subnet=dict(by_subnet),
    )
