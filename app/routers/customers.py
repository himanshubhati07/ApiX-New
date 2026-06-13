# Customer endpoints excluding creation.
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.auth import get_current_user
from ..database import get_db
from ..models import ActivityAction, ActivityLog, Customer, Interaction, User
from ..schemas import CustomerOut, CustomerUpdate

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("", response_model=list[CustomerOut])
async def list_customers(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[CustomerOut]:
    result = await db.execute(select(Customer).offset(offset).limit(limit))
    return result.scalars().all()


@router.get("/{customer_id}", response_model=CustomerOut)
async def get_customer(
    customer_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CustomerOut:
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return customer


@router.patch("/{customer_id}", response_model=CustomerOut)
async def update_customer(
    customer_id: str,
    payload: CustomerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CustomerOut:
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(customer, field, value)
    customer.updated_at = datetime.utcnow()
    log = ActivityLog(
        action=ActivityAction.customer_update,
        actor_user_id=current_user.id,
        customer_id=customer.id,
        details="Customer updated",
    )
    db.add(log)
    await db.commit()
    await db.refresh(customer)
    return customer


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    interaction_ids = select(Interaction.id).where(Interaction.customer_id == customer.id)
    await db.execute(
        update(ActivityLog).where(ActivityLog.customer_id == customer.id).values(customer_id=None)
    )
    await db.execute(
        update(ActivityLog)
        .where(ActivityLog.interaction_id.in_(interaction_ids))
        .values(interaction_id=None)
    )
    await db.delete(customer)
    log = ActivityLog(
        action=ActivityAction.customer_delete,
        actor_user_id=current_user.id,
        customer_id=None,
        details=f"Customer {customer.id} deleted",
    )
    db.add(log)
    await db.commit()
    return None
