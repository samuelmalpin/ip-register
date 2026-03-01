"""add subnet dhcp range and unknown ip status

Revision ID: 0002_dhcp_unknown
Revises: 0001_initial
Create Date: 2026-03-01
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_dhcp_unknown"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("subnets", sa.Column("dhcp_start", sa.String(length=64), nullable=True))
    op.add_column("subnets", sa.Column("dhcp_end", sa.String(length=64), nullable=True))
    op.execute("ALTER TYPE ipstatus ADD VALUE IF NOT EXISTS 'UNKNOWN'")


def downgrade() -> None:
    op.drop_column("subnets", "dhcp_end")
    op.drop_column("subnets", "dhcp_start")
