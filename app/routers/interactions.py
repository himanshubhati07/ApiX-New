# Interaction endpoints for customer communications.
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.auth import get_current_user
from ..database import get_db
from ..models import ActivityAction, ActivityLog, Customer, Interaction, User
from ..schemas import InteractionCreate, InteractionOut, InteractionUpdate

router = APIRouter(prefix="/interactions", tags=["interactions"])


@router.post("", response_model=InteractionOut, status_code=status.HTTP_201_CREATED)
async def create_interaction(
    payload: InteractionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InteractionOut:
    customer = await db.execute(select(Customer).where(Customer.id == payload.customer_id))
    if not customer.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    interaction = Interaction(
        customer_id=payload.customer_id,
        channel=payload.channel,
        subject=payload.subject,
        content=payload.content,
        occurred_at=payload.occurred_at or datetime.utcnow(),
    )
    db.add(interaction)
    await db.flush()
    log = ActivityLog(
        action=ActivityAction.interaction_create,
        actor_user_id=current_user.id,
        customer_id=payload.customer_id,
        interaction_id=interaction.id,
        details="Interaction created",
    )
    db.add(log)
    await db.commit()
    await db.refresh(interaction)
    return interaction


@router.get("", response_model=list[InteractionOut])
async def list_interactions(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[InteractionOut]:
    result = await db.execute(select(Interaction).offset(offset).limit(limit))
    return result.scalars().all()


@router.get("/{interaction_id}", response_model=InteractionOut)
async def get_interaction(
    interaction_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InteractionOut:
    result = await db.execute(select(Interaction).where(Interaction.id == interaction_id))
    interaction = result.scalar_one_or_none()
    if not interaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interaction not found")
    return interaction


@router.patch("/{interaction_id}", response_model=InteractionOut)
async def update_interaction(
    interaction_id: str,
    payload: InteractionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InteractionOut:
    result = await db.execute(select(Interaction).where(Interaction.id == interaction_id))
    interaction = result.scalar_one_or_none()
    if not interaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interaction not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(interaction, field, value)
    interaction.updated_at = datetime.utcnow()
    log = ActivityLog(
        action=ActivityAction.interaction_update,
        actor_user_id=current_user.id,
        customer_id=interaction.customer_id,
        interaction_id=interaction.id,
        details="Interaction updated",
    )
    db.add(log)
    await db.commit()
    await db.refresh(interaction)
    return interaction


@router.delete("/{interaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_interaction(
    interaction_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    result = await db.execute(select(Interaction).where(Interaction.id == interaction_id))
    interaction = result.scalar_one_or_none()
    if not interaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interaction not found")
    await db.execute(
        update(ActivityLog)
        .where(ActivityLog.interaction_id == interaction.id)
        .values(interaction_id=None)
    )
    await db.delete(interaction)
    log = ActivityLog(
        action=ActivityAction.interaction_delete,
        actor_user_id=current_user.id,
        customer_id=interaction.customer_id,
        interaction_id=None,
        details=f"Interaction {interaction.id} deleted",
    )
    db.add(log)
    await db.commit()
    return None
