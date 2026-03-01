"""initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2026-02-28
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", sa.Enum("ADMIN", "VIEWER", name="userrole"), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("refresh_token_hash", sa.String(length=255), nullable=True),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "sites",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=False),
    )
    op.create_index("ix_sites_name", "sites", ["name"], unique=True)

    op.create_table(
        "subnets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cidr", sa.String(length=64), nullable=False),
        sa.Column("site_id", sa.Integer(), sa.ForeignKey("sites.id", ondelete="CASCADE"), nullable=False),
    )
    op.create_index("ix_subnets_cidr", "subnets", ["cidr"], unique=False)
    op.create_index("ix_subnets_site_id", "subnets", ["site_id"], unique=False)

    op.create_table(
        "ip_addresses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("address", sa.String(length=64), nullable=False),
        sa.Column("status", sa.Enum("FREE", "RESERVED", "STATIC", "DHCP", "CONFLICT", name="ipstatus"), nullable=False),
        sa.Column("hostname", sa.String(length=255), nullable=True),
        sa.Column("mac_address", sa.String(length=64), nullable=True),
        sa.Column("site_id", sa.Integer(), sa.ForeignKey("sites.id", ondelete="CASCADE"), nullable=False),
        sa.Column("subnet_id", sa.Integer(), sa.ForeignKey("subnets.id", ondelete="CASCADE"), nullable=False),
        sa.UniqueConstraint("address", "site_id", name="uq_ip_per_site"),
    )
    op.create_index("ix_ip_addresses_address", "ip_addresses", ["address"], unique=False)
    op.create_index("ix_ip_addresses_site_id", "ip_addresses", ["site_id"], unique=False)
    op.create_index("ix_ip_addresses_subnet_id", "ip_addresses", ["subnet_id"], unique=False)

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(length=120), nullable=False),
        sa.Column("entity", sa.String(length=120), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"], unique=False)
    op.create_index("ix_audit_logs_entity", "audit_logs", ["entity"], unique=False)
    op.create_index("ix_audit_logs_timestamp", "audit_logs", ["timestamp"], unique=False)


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("ip_addresses")
    op.drop_table("subnets")
    op.drop_table("sites")
    op.drop_table("users")
