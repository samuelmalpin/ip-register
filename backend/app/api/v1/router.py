from fastapi import APIRouter
from app.api.v1.endpoints import auth, dashboard, ips, scan, sites, subnets, users


api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(sites.router)
api_router.include_router(subnets.router)
api_router.include_router(ips.router)
api_router.include_router(scan.router)
api_router.include_router(dashboard.router)
