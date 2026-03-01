import ipaddress
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ip_address import IPAddress, IPStatus
from app.models.subnet import Subnet


async def suggest_free_ip(db: AsyncSession, subnet_id: int, gateway_ip: str | None = None) -> str:
    subnet = await db.get(Subnet, subnet_id)
    if not subnet:
        raise ValueError("Subnet not found")

    network = ipaddress.ip_network(subnet.cidr, strict=False)

    query = select(IPAddress.address).where(IPAddress.subnet_id == subnet_id)
    result = await db.execute(query)
    used = {ipaddress.ip_address(row[0]) for row in result.all()}

    excluded = {network.network_address, network.broadcast_address}
    if gateway_ip:
        excluded.add(ipaddress.ip_address(gateway_ip))

    for host in network.hosts():
        if host in excluded:
            continue
        if host not in used:
            return str(host)

    raise ValueError("No free IP available")


def detect_conflict(existing_ips: set[str], scanned_ip: str) -> IPStatus:
    return IPStatus.CONFLICT if scanned_ip in existing_ips else IPStatus.DHCP
