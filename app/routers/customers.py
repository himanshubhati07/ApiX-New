from dotenv import load_dotenv
load_dotenv('.env_dbf2ee37-0d53-416c-8916-7748075b87f8', override=True)

import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user, require_roles
from app.database import get_db
from app.models import Customer, CustomerStatusEnum, CustomerTypeEnum, RoleEnum
from app.schemas import CustomerCreate, CustomerRead, CustomerUpdate, CustomerListResponse
from app.services import record_audit_log, record_activity

router = APIRouter(prefix="/api/v1/customers", tags=["Customers"])


@router.post("", response_model=CustomerRead, status_code=status.HTTP_201_CREATED)
async def create_customer(
    payload: CustomerCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles(RoleEnum.admin, RoleEnum.manager)),
):
    existing = await db.execute(select(Customer).where(Customer.email == payload.email))
    if existing.scalars().first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Customer email already exists")

    customer = Customer(
        customer_id=f"CUST-{uuid.uuid4().hex[:8]}",
        name=payload.name,
        email=payload.email,
        phone_number=payload.phone_number,
        customer_type=payload.customer_type,
        status=payload.status,
        created_at=datetime.utcnow(),
    )
    db.add(customer)
    await db.flush()
    await record_audit_log(
        db,
        actor_id=current_user.id,
        entity_type="customer",
        entity_id=customer.id,
        action="create",
        change_summary=f"Created customer {customer.name}",
    )
    await record_activity(db, customer_id=customer.id, action="customer_created")
    await db.commit()
    await db.refresh(customer)
    return customer


@router.get("", response_model=CustomerListResponse)
async def list_customers(
    name: str | None = Query(default=None),
    status_filter: CustomerStatusEnum | None = Query(default=None, alias="status"),
    customer_type: CustomerTypeEnum | None = Query(default=None, alias="type"),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = select(Customer)
    if name:
        query = query.where(Customer.name.ilike(f"%{name}%"))
    if status_filter:
        query = query.where(Customer.status == status_filter)
    if customer_type:
        query = query.where(Customer.customer_type == customer_type)
    if start_date:
        query = query.where(Customer.created_at >= start_date)
    if end_date:
        query = query.where(Customer.created_at <= end_date)

    sort_map = {
        "name": Customer.name,
        "created_at": Customer.created_at,
        "status": Customer.status,
        "customer_type": Customer.customer_type,
    }
    sort_column = sort_map.get(sort_by, Customer.created_at)
    if sort_order.lower() == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    total = await db.execute(select(func.count()).select_from(query.subquery()))
    total_count = total.scalar_one()

    result = await db.execute(query.offset((page - 1) * page_size).limit(page_size))
    customers = result.scalars().unique().all()

    return CustomerListResponse(total=total_count, page=page, page_size=page_size, items=customers)


@router.get("/{customer_id}", response_model=CustomerRead)
async def get_customer(
    customer_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalars().first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return customer


@router.put("/{customer_id}", response_model=CustomerRead)
async def update_customer(
    customer_id: str,
    payload: CustomerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles(RoleEnum.admin, RoleEnum.manager)),
):
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalars().first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    updates = payload.dict(exclude_unset=True)
    for field, value in updates.items():
        setattr(customer, field, value)

    await record_audit_log(
        db,
        actor_id=current_user.id,
        entity_type="customer",
        entity_id=customer.id,
        action="update",
        change_summary=f"Updated fields: {', '.join(updates.keys())}",
    )
    await record_activity(db, customer_id=customer.id, action="customer_updated", details=str(updates))
    await db.commit()
    await db.refresh(customer)
    return customer


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles(RoleEnum.admin, RoleEnum.manager)),
):
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalars().first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    await record_audit_log(
        db,
        actor_id=current_user.id,
        entity_type="customer",
        entity_id=customer.id,
        action="delete",
        change_summary=f"Deleted customer {customer.name}",
    )
    await record_activity(db, customer_id=customer.id, action="customer_deleted")
    await db.delete(customer)
    await db.commit()
    return None
