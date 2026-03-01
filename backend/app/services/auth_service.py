from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User, UserRole


async def register_user(db: AsyncSession, email: str, password: str, role: UserRole) -> User:
    result = await db.execute(select(User).where(User.email == email))
    existing = result.scalar_one_or_none()
    if existing:
        raise ValueError("Email already registered")

    user = User(email=email, hashed_password=get_password_hash(password), role=role)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User:
    result = await db.execute(select(User).where(User.email == email, User.is_active.is_(True)))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        raise ValueError("Invalid credentials")
    return user


async def issue_tokens(db: AsyncSession, user: User) -> tuple[str, str]:
    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    user.refresh_token_hash = get_password_hash(refresh_token)
    await db.commit()
    return access_token, refresh_token


async def rotate_refresh_token(db: AsyncSession, user: User, provided_token: str) -> tuple[str, str]:
    if not user.refresh_token_hash or not verify_password(provided_token, user.refresh_token_hash):
        raise ValueError("Invalid refresh token")

    return await issue_tokens(db, user)
