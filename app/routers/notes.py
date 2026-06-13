from dotenv import load_dotenv
load_dotenv('.env_dbf2ee37-0d53-416c-8916-7748075b87f8', override=True)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user, require_roles
from app.database import get_db
from app.models import Customer, CustomerNote, RoleEnum
from app.schemas import CustomerNoteCreate, CustomerNoteRead, CustomerNoteUpdate
from app.services import record_audit_log, record_activity

router = APIRouter(prefix="/api/v1", tags=["Customer Notes"])


@router.post("/customers/{customer_id}/notes", response_model=CustomerNoteRead, status_code=status.HTTP_201_CREATED)
async def create_note(
    customer_id: str,
    payload: CustomerNoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    customer_result = await db.execute(select(Customer).where(Customer.id == customer_id))
    if not customer_result.scalars().first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    note = CustomerNote(customer_id=customer_id, note=payload.note)
    db.add(note)
    await db.flush()
    await record_audit_log(
        db,
        actor_id=current_user.id,
        entity_type="note",
        entity_id=note.id,
        action="create",
        change_summary="Added customer note",
    )
    await record_activity(db, customer_id=customer_id, action="note_added")
    await db.commit()
    await db.refresh(note)
    return note


@router.get("/customers/{customer_id}/notes", response_model=list[CustomerNoteRead])
async def list_notes(
    customer_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(select(CustomerNote).where(CustomerNote.customer_id == customer_id))
    return result.scalars().all()


@router.get("/notes/{note_id}", response_model=CustomerNoteRead)
async def get_note(
    note_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(select(CustomerNote).where(CustomerNote.id == note_id))
    note = result.scalars().first()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


@router.put("/notes/{note_id}", response_model=CustomerNoteRead)
async def update_note(
    note_id: str,
    payload: CustomerNoteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles(RoleEnum.admin, RoleEnum.manager)),
):
    result = await db.execute(select(CustomerNote).where(CustomerNote.id == note_id))
    note = result.scalars().first()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    updates = payload.dict(exclude_unset=True)
    for field, value in updates.items():
        setattr(note, field, value)

    await record_audit_log(
        db,
        actor_id=current_user.id,
        entity_type="note",
        entity_id=note.id,
        action="update",
        change_summary=f"Updated note fields: {', '.join(updates.keys())}",
    )
    await record_activity(db, customer_id=note.customer_id, action="note_updated", details=str(updates))
    await db.commit()
    await db.refresh(note)
    return note


@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles(RoleEnum.admin, RoleEnum.manager)),
):
    result = await db.execute(select(CustomerNote).where(CustomerNote.id == note_id))
    note = result.scalars().first()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    await record_audit_log(
        db,
        actor_id=current_user.id,
        entity_type="note",
        entity_id=note.id,
        action="delete",
        change_summary="Deleted note",
    )
    await record_activity(db, customer_id=note.customer_id, action="note_deleted")
    await db.delete(note)
    await db.commit()
    return None
