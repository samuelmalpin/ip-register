from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.database import AsyncSessionLocal
from app.core.logging import logger
from app.core.middleware import CSRFMiddleware, RateLimitMiddleware, add_security_headers
from app.core.security import get_password_hash, verify_password
from app.models.user import User, UserRole

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == settings.admin_email))
        admin = result.scalar_one_or_none()
        if not admin:
            db.add(
                User(
                    email=settings.admin_email,
                    hashed_password=get_password_hash(settings.admin_password),
                    role=UserRole.ADMIN,
                    is_active=True,
                    must_change_credentials=True,
                )
            )
            await db.commit()
            logger.info("Default admin user created")
        elif (
            admin.role == UserRole.ADMIN
            and admin.email == settings.admin_email
            and verify_password(settings.admin_password, admin.hashed_password)
            and not admin.must_change_credentials
        ):
            admin.must_change_credentials = True
            await db.commit()
            logger.info("Default admin first-login setup enforced")
    yield


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.parsed_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-CSRF-Token"],
)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(CSRFMiddleware)
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.middleware("http")
async def security_headers_middleware(request, call_next):
    response = await call_next(request)
    return add_security_headers(response)


@app.get("/health")
async def health_check():
    return {"status": "ok", "environment": settings.environment}
