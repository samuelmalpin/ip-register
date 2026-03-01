from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.site import Site
from app.models.user import User, UserRole
from app.schemas.site import SiteCreate, SiteResponse, SiteUpdate
from app.utils.audit import add_audit_log
from app.utils.sanitize import sanitize_text


router = APIRouter(prefix="/sites", tags=["sites"])


@router.get("", response_model=list[SiteResponse])
async def list_sites(
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Site).order_by(Site.name.asc()))
    return result.scalars().all()


@router.post("", response_model=SiteResponse, status_code=status.HTTP_201_CREATED)
async def create_site(
    payload: SiteCreate,
    user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    site = Site(name=sanitize_text(payload.name, 120), location=sanitize_text(payload.location, 255))
    db.add(site)
    await db.commit()
    await db.refresh(site)
    await add_audit_log(db, user.id, "CREATE", "Site", site.id)
    return site


@router.patch("/{site_id}", response_model=SiteResponse)
async def update_site(
    site_id: int,
    payload: SiteUpdate,
    user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    site = await db.get(Site, site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    if payload.name is not None:
        site.name = sanitize_text(payload.name, 120)
    if payload.location is not None:
        site.location = sanitize_text(payload.location, 255)

    await db.commit()
    await db.refresh(site)
    await add_audit_log(db, user.id, "UPDATE", "Site", site.id)
    return site


@router.delete("/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_site(
    site_id: int,
    user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    site = await db.get(Site, site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    await db.delete(site)
    await db.commit()
    await add_audit_log(db, user.id, "DELETE", "Site", site_id)
    return None
