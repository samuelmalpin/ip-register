"""add must_change_credentials to users

Revision ID: 0003_first_login
Revises: 0002_dhcp_unknown
Create Date: 2026-03-01
"""

from alembic import op
import sqlalchemy as sa

revision = "0003_first_login"
down_revision = "0002_dhcp_unknown"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("must_change_credentials", sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    op.drop_column("users", "must_change_credentials")
