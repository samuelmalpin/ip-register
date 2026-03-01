import asyncio
import ipaddress
import re
from app.models.ip_address import IPStatus


IP_PATTERN = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")


async def run_nmap_scan(cidr: str) -> list[str]:
    process = await asyncio.create_subprocess_exec(
        "nmap",
        "-sn",
        cidr,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise RuntimeError(f"nmap scan failed: {stderr.decode('utf-8', errors='ignore')}")

    text = stdout.decode("utf-8", errors="ignore")
    return list(dict.fromkeys(IP_PATTERN.findall(text)))


def map_scan_result(existing_ips: set[str], scanned_ips: list[str]) -> list[dict]:
    results = []
    for ip in scanned_ips:
        status = IPStatus.CONFLICT.value if ip in existing_ips else IPStatus.UNKNOWN.value
        results.append({"address": ip, "status": status, "mac_address": None})
    return results


def apply_dhcp_range_status(
    results: list[dict],
    dhcp_start: str | None,
    dhcp_end: str | None,
) -> list[dict]:
    if not dhcp_start or not dhcp_end:
        return results

    start = int(ipaddress.ip_address(dhcp_start))
    end = int(ipaddress.ip_address(dhcp_end))
    for row in results:
        current = int(ipaddress.ip_address(row["address"]))
        row["status"] = IPStatus.DHCP.value if start <= current <= end else IPStatus.UNKNOWN.value
    return results


def resolve_mac_addresses(ip_addresses: list[str]) -> dict[str, str]:
    if not ip_addresses:
        return {}

    try:
        from scapy.all import ARP, Ether, srp

        packet = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip_addresses)
        answered, _ = srp(packet, timeout=2, verbose=0)
        return {received.psrc: received.hwsrc for _, received in answered}
    except Exception:
        return {}
