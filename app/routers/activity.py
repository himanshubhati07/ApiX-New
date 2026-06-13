# Activity log endpoints.
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.auth import get_current_user
from ..database import get_db
from ..models import ActivityLog, User
from ..schemas import ActivityLogOut

router = APIRouter(prefix="/activity", tags=["activity"])


@router.get("", response_model=list[ActivityLogOut])
async def list_activity(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ActivityLogOut]:
    result = await db.execute(select(ActivityLog).offset(offset).limit(limit))
    return result.scalars().all()


@router.get("/{activity_id}", response_model=ActivityLogOut)
async def get_activity(
    activity_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ActivityLogOut:
    result = await db.execute(select(ActivityLog).where(ActivityLog.id == activity_id))
    activity = result.scalar_one_or_none()
    if not activity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity log not found")
    return activity
