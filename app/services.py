from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AuditLog, CustomerActivity


async def record_audit_log(
    db: AsyncSession,
    *,
    actor_id: Optional[str],
    entity_type: str,
    entity_id: str,
    action: str,
    change_summary: Optional[str] = None,
):
    log = AuditLog(
        actor_id=actor_id,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        change_summary=change_summary,
        created_at=datetime.utcnow(),
    )
    db.add(log)


async def record_activity(
    db: AsyncSession,
    *,
    customer_id: str,
    action: str,
    details: Optional[str] = None,
):
    activity = CustomerActivity(
        customer_id=customer_id,
        action=action,
        details=details,
        created_at=datetime.utcnow(),
    )
    db.add(activity)
