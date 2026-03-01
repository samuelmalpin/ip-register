from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Site(Base):
    __tablename__ = "sites"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    location: Mapped[str] = mapped_column(String(255))

    subnets = relationship("Subnet", back_populates="site", cascade="all, delete-orphan")
    ip_addresses = relationship("IPAddress", back_populates="site", cascade="all, delete-orphan")
