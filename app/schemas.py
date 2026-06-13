from dotenv import load_dotenv
load_dotenv('.env_dbf2ee37-0d53-416c-8916-7748075b87f8', override=True)

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.models import CustomerStatusEnum, CustomerTypeEnum, RoleEnum


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: RoleEnum = RoleEnum.user


class UserRead(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: RoleEnum
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AddressBase(BaseModel):
    line1: str
    line2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str


class AddressCreate(AddressBase):
    pass


class AddressUpdate(BaseModel):
    line1: Optional[str] = None
    line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None


class AddressRead(AddressBase):
    id: str
    customer_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ContactPersonBase(BaseModel):
    name: str
    email: EmailStr
    phone_number: str
    title: Optional[str] = None


class ContactPersonCreate(ContactPersonBase):
    pass


class ContactPersonUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    title: Optional[str] = None


class ContactPersonRead(ContactPersonBase):
    id: str
    customer_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CustomerNoteBase(BaseModel):
    note: str = Field(..., min_length=1)


class CustomerNoteCreate(CustomerNoteBase):
    pass


class CustomerNoteUpdate(BaseModel):
    note: Optional[str] = None


class CustomerNoteRead(CustomerNoteBase):
    id: str
    customer_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CustomerActivityRead(BaseModel):
    id: str
    customer_id: str
    action: str
    details: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CustomerBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    phone_number: str
    customer_type: CustomerTypeEnum
    status: CustomerStatusEnum = CustomerStatusEnum.active


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    customer_type: Optional[CustomerTypeEnum] = None
    status: Optional[CustomerStatusEnum] = None


class CustomerRead(CustomerBase):
    id: str
    customer_id: str
    created_at: datetime
    addresses: List[AddressRead] = []
    contacts: List[ContactPersonRead] = []
    notes: List[CustomerNoteRead] = []

    model_config = ConfigDict(from_attributes=True)


class CustomerListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[CustomerRead]


class AuditLogRead(BaseModel):
    id: str
    actor_id: Optional[str] = None
    entity_type: str
    entity_id: str
    action: str
    change_summary: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
