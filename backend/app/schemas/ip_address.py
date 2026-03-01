import ipaddress
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.models.ip_address import IPStatus


class IPAddressBase(BaseModel):
    address: str
    status: IPStatus = IPStatus.RESERVED
    hostname: str | None = Field(default=None, max_length=255)
    mac_address: str | None = Field(default=None, max_length=64)
    site_id: int
    subnet_id: int

    @field_validator("address")
    @classmethod
    def validate_ip(cls, value: str) -> str:
        ipaddress.ip_address(value)
        return value


class IPAddressCreate(IPAddressBase):
    pass


class IPAddressUpdate(BaseModel):
    status: IPStatus | None = None
    hostname: str | None = Field(default=None, max_length=255)
    mac_address: str | None = Field(default=None, max_length=64)


class IPAddressResponse(IPAddressBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
