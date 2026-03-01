import enum
from sqlalchemy import Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class IPStatus(str, enum.Enum):
    FREE = "FREE"
    RESERVED = "RESERVED"
    STATIC = "STATIC"
    DHCP = "DHCP"
    CONFLICT = "CONFLICT"
    UNKNOWN = "UNKNOWN"


class IPAddress(Base):
    __tablename__ = "ip_addresses"
    __table_args__ = (UniqueConstraint("address", "site_id", name="uq_ip_per_site"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    address: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[IPStatus] = mapped_column(Enum(IPStatus), default=IPStatus.FREE)
    hostname: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mac_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    site_id: Mapped[int] = mapped_column(ForeignKey("sites.id", ondelete="CASCADE"), index=True)
    subnet_id: Mapped[int] = mapped_column(ForeignKey("subnets.id", ondelete="CASCADE"), index=True)

    site = relationship("Site", back_populates="ip_addresses")
    subnet = relationship("Subnet", back_populates="ip_addresses")
