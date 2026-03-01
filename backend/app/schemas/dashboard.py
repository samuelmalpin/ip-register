from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_ips: int
    used_ips: int
    free_ips: int
    free_percentage: float
    by_site: dict[str, int]
    by_subnet: dict[str, int]
