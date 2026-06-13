from dotenv import load_dotenv
load_dotenv('.env_dbf2ee37-0d53-416c-8916-7748075b87f8', override=True)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user, require_roles
from app.database import get_db
from app.models import ContactPerson, Customer, CustomerTypeEnum, RoleEnum
from app.schemas import ContactPersonCreate, ContactPersonRead, ContactPersonUpdate
from app.services import record_audit_log, record_activity

router = APIRouter(prefix="/api/v1", tags=["Contact Persons"])


def ensure_business_customer(customer: Customer):
    if customer.customer_type != CustomerTypeEnum.business:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Contacts are only allowed for business customers")


@router.post("/customers/{customer_id}/contacts", response_model=ContactPersonRead, status_code=status.HTTP_201_CREATED)
async def create_contact(
    customer_id: str,
    payload: ContactPersonCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles(RoleEnum.admin, RoleEnum.manager)),
):
    customer_result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = customer_result.scalars().first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    ensure_business_customer(customer)

    contact = ContactPerson(customer_id=customer_id, **payload.dict())
    db.add(contact)
    await db.flush()
    await record_audit_log(
        db,
        actor_id=current_user.id,
        entity_type="contact",
        entity_id=contact.id,
        action="create",
        change_summary=f"Added contact to customer {customer_id}",
    )
    await record_activity(db, customer_id=customer_id, action="contact_added")
    await db.commit()
    await db.refresh(contact)
    return contact


@router.get("/customers/{customer_id}/contacts", response_model=list[ContactPersonRead])
async def list_contacts(
    customer_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(select(ContactPerson).where(ContactPerson.customer_id == customer_id))
    return result.scalars().all()


@router.get("/contacts/{contact_id}", response_model=ContactPersonRead)
async def get_contact(
    contact_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(select(ContactPerson).where(ContactPerson.id == contact_id))
    contact = result.scalars().first()
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.put("/contacts/{contact_id}", response_model=ContactPersonRead)
async def update_contact(
    contact_id: str,
    payload: ContactPersonUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles(RoleEnum.admin, RoleEnum.manager)),
):
    result = await db.execute(select(ContactPerson).where(ContactPerson.id == contact_id))
    contact = result.scalars().first()
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")

    updates = payload.dict(exclude_unset=True)
    for field, value in updates.items():
        setattr(contact, field, value)

    await record_audit_log(
        db,
        actor_id=current_user.id,
        entity_type="contact",
        entity_id=contact.id,
        action="update",
        change_summary=f"Updated contact fields: {', '.join(updates.keys())}",
    )
    await record_activity(db, customer_id=contact.customer_id, action="contact_updated", details=str(updates))
    await db.commit()
    await db.refresh(contact)
    return contact


@router.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles(RoleEnum.admin, RoleEnum.manager)),
):
    result = await db.execute(select(ContactPerson).where(ContactPerson.id == contact_id))
    contact = result.scalars().first()
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")

    await record_audit_log(
        db,
        actor_id=current_user.id,
        entity_type="contact",
        entity_id=contact.id,
        action="delete",
        change_summary="Deleted contact",
    )
    await record_activity(db, customer_id=contact.customer_id, action="contact_deleted")
    await db.delete(contact)
    await db.commit()
    return None
