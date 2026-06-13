from dotenv import load_dotenv
load_dotenv('.env_dbf2ee37-0d53-416c-8916-7748075b87f8', override=True)

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.models import CustomerActivity
from app.schemas import CustomerActivityRead

router = APIRouter(prefix="/api/v1", tags=["Customer Activities"])


@router.get("/customers/{customer_id}/activities", response_model=list[CustomerActivityRead])
async def list_activities(
    customer_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(select(CustomerActivity).where(CustomerActivity.customer_id == customer_id))
    return result.scalars().all()
