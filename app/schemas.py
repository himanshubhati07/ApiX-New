# Pydantic schemas for request/response payloads.
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from .models import ActivityAction, CustomerStatus, InteractionChannel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: str


class UserBase(BaseModel):
    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserOut(UserBase):
    id: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CustomerBase(BaseModel):
    external_id: str = Field(min_length=3, max_length=64)
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    status: CustomerStatus = CustomerStatus.active
    address: Optional[str] = None
    notes: Optional[str] = None


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    status: Optional[CustomerStatus] = None
    address: Optional[str] = None
    notes: Optional[str] = None


class CustomerOut(CustomerBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InteractionBase(BaseModel):
    customer_id: str
    channel: InteractionChannel
    subject: str
    content: str
    occurred_at: Optional[datetime] = None


class InteractionCreate(InteractionBase):
    pass


class InteractionUpdate(BaseModel):
    channel: Optional[InteractionChannel] = None
    subject: Optional[str] = None
    content: Optional[str] = None
    occurred_at: Optional[datetime] = None


class InteractionOut(InteractionBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ActivityLogOut(BaseModel):
    id: str
    action: ActivityAction
    actor_user_id: str
    customer_id: Optional[str] = None
    interaction_id: Optional[str] = None
    details: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
