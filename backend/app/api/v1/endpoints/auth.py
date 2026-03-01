import secrets
from fastapi import APIRouter, Depends, HTTPException, Response, status, Cookie
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.config import get_settings
from app.core.security import TokenType, decode_token, get_password_hash, verify_password
from app.models.user import User, UserRole
from app.schemas.auth import ChangePasswordRequest, FirstLoginSetupRequest, LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.services.auth_service import authenticate_user, issue_tokens, register_user, rotate_refresh_token
from app.utils.audit import add_audit_log


router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    user = await register_user(db, payload.email.lower(), payload.password, UserRole.VIEWER)
    await add_audit_log(db, user.id, "REGISTER", "User", user.id)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    try:
        user = await authenticate_user(db, payload.email.lower(), payload.password)
        access_token, refresh_token = await issue_tokens(db, user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    csrf_token = secrets.token_urlsafe(32)

    response.set_cookie("access_token", access_token, httponly=True, secure=settings.cookie_secure, samesite="strict", max_age=900)
    response.set_cookie("refresh_token", refresh_token, httponly=True, secure=settings.cookie_secure, samesite="strict", max_age=604800)
    response.set_cookie("csrf_token", csrf_token, httponly=False, secure=settings.cookie_secure, samesite="strict", max_age=604800)

    await add_audit_log(db, user.id, "LOGIN", "User", user.id)
    return TokenResponse(message="Login successful")


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(
    response: Response,
    refresh_token: str | None = Cookie(default=None, alias="refresh_token"),
    db: AsyncSession = Depends(get_db),
):
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token")

    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != TokenType.REFRESH:
            raise ValueError("Invalid refresh token type")
        user_id = int(payload.get("sub"))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from exc

    result = await db.execute(select(User).where(User.id == user_id, User.is_active.is_(True)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    try:
        access_token, new_refresh_token = await rotate_refresh_token(db, user, refresh_token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    response.set_cookie("access_token", access_token, httponly=True, secure=settings.cookie_secure, samesite="strict", max_age=900)
    response.set_cookie("refresh_token", new_refresh_token, httponly=True, secure=settings.cookie_secure, samesite="strict", max_age=604800)
    return TokenResponse(message="Tokens refreshed")


@router.post("/logout", response_model=TokenResponse)
async def logout(response: Response, db: AsyncSession = Depends(get_db), access_token: str | None = Cookie(None)):
    user_id = None
    if access_token:
        try:
            payload = decode_token(access_token)
            user_id = int(payload.get("sub"))
        except Exception:
            user_id = None

    if user_id:
        user = await db.get(User, user_id)
        if user:
            user.refresh_token_hash = None
            await db.commit()
            await add_audit_log(db, user.id, "LOGOUT", "User", user.id)

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    response.delete_cookie("csrf_token")
    return TokenResponse(message="Logged out")


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/change-password", response_model=TokenResponse)
async def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")
    if payload.current_password == payload.new_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password must be different")

    current_user.hashed_password = get_password_hash(payload.new_password)
    current_user.refresh_token_hash = None
    await db.commit()
    await add_audit_log(db, current_user.id, "CHANGE_PASSWORD", "User", current_user.id)
    return TokenResponse(message="Password changed successfully")


@router.post("/first-login-setup", response_model=TokenResponse)
async def first_login_setup(
    payload: FirstLoginSetupRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can use this endpoint")
    if not current_user.must_change_credentials:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="First login setup not required")
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")
    if payload.current_password == payload.new_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password must be different")

    normalized_email = payload.new_email.lower()
    if normalized_email != current_user.email:
        result = await db.execute(select(User).where(User.email == normalized_email, User.id != current_user.id))
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")

    current_user.email = normalized_email
    current_user.hashed_password = get_password_hash(payload.new_password)
    current_user.must_change_credentials = False
    current_user.refresh_token_hash = None
    await db.commit()
    await add_audit_log(db, current_user.id, "FIRST_LOGIN_SETUP", "User", current_user.id)

    return TokenResponse(message="Admin credentials updated successfully")
