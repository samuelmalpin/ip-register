from pydantic import BaseModel, ConfigDict, Field, field_validator
import ipaddress


class SubnetBase(BaseModel):
    cidr: str = Field(min_length=9, max_length=64)
    site_id: int
    dhcp_start: str | None = None
    dhcp_end: str | None = None

    @field_validator("cidr")
    @classmethod
    def validate_cidr(cls, value: str) -> str:
        ipaddress.ip_network(value, strict=False)
        return value

    @field_validator("dhcp_start", "dhcp_end")
    @classmethod
    def validate_ip_fields(cls, value: str | None) -> str | None:
        if value is not None:
            ipaddress.ip_address(value)
        return value


class SubnetCreate(SubnetBase):
    pass


class SubnetUpdate(BaseModel):
    cidr: str | None = None
    dhcp_start: str | None = None
    dhcp_end: str | None = None

    @field_validator("cidr")
    @classmethod
    def validate_cidr(cls, value: str | None) -> str | None:
        if value is not None:
            ipaddress.ip_network(value, strict=False)
        return value

    @field_validator("dhcp_start", "dhcp_end")
    @classmethod
    def validate_ip_fields(cls, value: str | None) -> str | None:
        if value is not None:
            ipaddress.ip_address(value)
        return value


class SubnetResponse(SubnetBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
