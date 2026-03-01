from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Subnet(Base):
    __tablename__ = "subnets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    cidr: Mapped[str] = mapped_column(String(64), index=True)
    site_id: Mapped[int] = mapped_column(ForeignKey("sites.id", ondelete="CASCADE"), index=True)
    dhcp_start: Mapped[str | None] = mapped_column(String(64), nullable=True)
    dhcp_end: Mapped[str | None] = mapped_column(String(64), nullable=True)

    site = relationship("Site", back_populates="subnets")
    ip_addresses = relationship("IPAddress", back_populates="subnet", cascade="all, delete-orphan")
