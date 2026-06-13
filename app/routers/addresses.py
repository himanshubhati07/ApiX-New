from dotenv import load_dotenv
load_dotenv('.env_dbf2ee37-0d53-416c-8916-7748075b87f8', override=True)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user, require_roles
from app.database import get_db
from app.models import Address, Customer, RoleEnum
from app.schemas import AddressCreate, AddressRead, AddressUpdate
from app.services import record_audit_log, record_activity

router = APIRouter(prefix="/api/v1", tags=["Addresses"])


@router.post("/customers/{customer_id}/addresses", response_model=AddressRead, status_code=status.HTTP_201_CREATED)
async def create_address(
    customer_id: str,
    payload: AddressCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles(RoleEnum.admin, RoleEnum.manager)),
):
    customer_result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = customer_result.scalars().first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    address = Address(customer_id=customer_id, **payload.dict())
    db.add(address)
    await db.flush()
    await record_audit_log(
        db,
        actor_id=current_user.id,
        entity_type="address",
        entity_id=address.id,
        action="create",
        change_summary=f"Added address to customer {customer_id}",
    )
    await record_activity(db, customer_id=customer_id, action="address_added")
    await db.commit()
    await db.refresh(address)
    return address


@router.get("/customers/{customer_id}/addresses", response_model=list[AddressRead])
async def list_addresses(
    customer_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(select(Address).where(Address.customer_id == customer_id))
    return result.scalars().all()


@router.get("/addresses/{address_id}", response_model=AddressRead)
async def get_address(
    address_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(select(Address).where(Address.id == address_id))
    address = result.scalars().first()
    if not address:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    return address


@router.put("/addresses/{address_id}", response_model=AddressRead)
async def update_address(
    address_id: str,
    payload: AddressUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles(RoleEnum.admin, RoleEnum.manager)),
):
    result = await db.execute(select(Address).where(Address.id == address_id))
    address = result.scalars().first()
    if not address:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")

    updates = payload.dict(exclude_unset=True)
    for field, value in updates.items():
        setattr(address, field, value)

    await record_audit_log(
        db,
        actor_id=current_user.id,
        entity_type="address",
        entity_id=address.id,
        action="update",
        change_summary=f"Updated address fields: {', '.join(updates.keys())}",
    )
    await record_activity(db, customer_id=address.customer_id, action="address_updated", details=str(updates))
    await db.commit()
    await db.refresh(address)
    return address


@router.delete("/addresses/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_address(
    address_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles(RoleEnum.admin, RoleEnum.manager)),
):
    result = await db.execute(select(Address).where(Address.id == address_id))
    address = result.scalars().first()
    if not address:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")

    await record_audit_log(
        db,
        actor_id=current_user.id,
        entity_type="address",
        entity_id=address.id,
        action="delete",
        change_summary="Deleted address",
    )
    await record_activity(db, customer_id=address.customer_id, action="address_deleted")
    await db.delete(address)
    await db.commit()
    return None
