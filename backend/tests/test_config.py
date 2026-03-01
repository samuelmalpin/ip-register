import pytest
from app.core.config import Settings


BASE_KWARGS = {
    'database_url': 'postgresql+asyncpg://ipam:ipam@db:5432/ipam',
    'jwt_secret_key': 'x' * 64,
    'admin_password': 'StrongPassword_123!',
}


def test_parsed_cors_origins_normalizes_and_deduplicates():
    settings = Settings(
        **BASE_KWARGS,
        cors_origins='https://example.com/, https://example.com, http://localhost:5173/'
    )

    assert settings.parsed_cors_origins() == ['https://example.com', 'http://localhost:5173']


def test_parsed_cors_origins_rejects_invalid_format():
    settings = Settings(**BASE_KWARGS, cors_origins='example.com')

    with pytest.raises(ValueError):
        settings.parsed_cors_origins()
