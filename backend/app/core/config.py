from functools import lru_cache
from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import urlparse


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "DevOps IPAM"
    environment: str = Field(default="dev", pattern="^(dev|prod|test)$")
    debug: bool = False

    api_v1_prefix: str = "/api/v1"
    frontend_url: AnyHttpUrl = "http://localhost:5173"

    database_url: str

    jwt_secret_key: str = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_minutes: int = 60 * 24 * 7
    cookie_secure: bool = True

    rate_limit_per_minute: int = 120
    csv_max_size_bytes: int = 2 * 1024 * 1024
    redis_url: str | None = None

    cors_origins: str = "http://localhost:5173"

    admin_email: str = Field(
        default="admin@example.com",
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
    )
    admin_password: str = Field(min_length=12)

    def parsed_cors_origins(self) -> list[str]:
        origins: list[str] = []
        for raw_item in self.cors_origins.split(","):
            item = raw_item.strip().rstrip("/")
            if not item:
                continue

            parsed = urlparse(item)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                raise ValueError(f"Invalid CORS origin format: {item}")
            origins.append(f"{parsed.scheme}://{parsed.netloc}")

        return list(dict.fromkeys(origins))


@lru_cache
def get_settings() -> Settings:
    return Settings()
