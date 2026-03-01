from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import require_role
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserPasswordReset, UserResponse, UserUpdate
from app.services.auth_service import register_user
from app.utils.audit import add_audit_log


router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserResponse])
async def list_users(
    _: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).order_by(User.id.asc()))
    return result.scalars().all()


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    admin: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    try:
        user = await register_user(db, payload.email.lower(), payload.password, payload.role)
    except ValueError as exc:
        if "already" in str(exc).lower():
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    await add_audit_log(db, admin.id, "CREATE", "User", user.id)
    return user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    payload: UserUpdate,
    admin: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if payload.role is not None:
        if user.role == UserRole.ADMIN and payload.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Admin role cannot be removed")
        user.role = payload.role
    if payload.is_active is not None:
        if user.role == UserRole.ADMIN and payload.is_active is False:
            raise HTTPException(status_code=403, detail="Admin user cannot be deactivated")
        user.is_active = payload.is_active

    await db.commit()
    await db.refresh(user)
    await add_audit_log(db, admin.id, "UPDATE", "User", user.id)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    admin: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role == UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin user cannot be deleted")

    await db.delete(user)
    await db.commit()
    await add_audit_log(db, admin.id, "DELETE", "User", user_id)
    return None


@router.post("/{user_id}/password", response_model=UserResponse)
async def reset_user_password(
    user_id: int,
    payload: UserPasswordReset,
    admin: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = get_password_hash(payload.new_password)
    user.refresh_token_hash = None
    await db.commit()
    await db.refresh(user)
    await add_audit_log(db, admin.id, "RESET_PASSWORD", "User", user.id)
    return user
