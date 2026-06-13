# Seed script to populate initial data.
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import Base, engine, SessionLocal
from app.models import Customer, CustomerStatus, Interaction, InteractionChannel, User
from app.core.security import get_password_hash

load_dotenv('.env_422ca5fd-04e6-47e0-a569-9b11c4768453', override=True)


async def seed_users(session: AsyncSession) -> list[User]:
    result = await session.execute(select(User))
    if result.scalars().all():
        result = await session.execute(select(User))
        return result.scalars().all()
    users = [
        User(email="admin@example.com", full_name="Admin User", hashed_password=get_password_hash("AdminPass123")),
        User(email="agent1@example.com", full_name="Agent One", hashed_password=get_password_hash("AgentPass123")),
        User(email="agent2@example.com", full_name="Agent Two", hashed_password=get_password_hash("AgentPass123")),
    ]
    session.add_all(users)
    await session.commit()
    return users


async def seed_customers(session: AsyncSession) -> list[Customer]:
    result = await session.execute(select(Customer))
    if result.scalars().all():
        result = await session.execute(select(Customer))
        return result.scalars().all()
    customers = [
        Customer(external_id="EXT-1001", name="Acme Corp", email="info@acme.com", phone="+1-555-1000"),
        Customer(external_id="EXT-1002", name="Globex", email="contact@globex.com", phone="+1-555-1001"),
        Customer(external_id="EXT-1003", name="Initech", email="hello@initech.com", phone="+1-555-1002", status=CustomerStatus.inactive),
    ]
    session.add_all(customers)
    await session.commit()
    return customers


async def seed_interactions(session: AsyncSession, customers: list[Customer]) -> None:
    result = await session.execute(select(Interaction))
    if result.scalars().all():
        return
    interactions = [
        Interaction(
            customer_id=customers[0].id,
            channel=InteractionChannel.email,
            subject="Welcome call",
            content="Discussed onboarding steps.",
            occurred_at=datetime.utcnow(),
        ),
        Interaction(
            customer_id=customers[1].id,
            channel=InteractionChannel.phone,
            subject="Support follow-up",
            content="Resolved billing issue.",
            occurred_at=datetime.utcnow(),
        ),
        Interaction(
            customer_id=customers[2].id,
            channel=InteractionChannel.meeting,
            subject="Renewal discussion",
            content="Reviewed renewal options.",
            occurred_at=datetime.utcnow(),
        ),
    ]
    session.add_all(interactions)
    await session.commit()


async def main() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)
    async with SessionLocal() as session:
        await seed_users(session)
        customers = await seed_customers(session)
        await seed_interactions(session, customers)


if __name__ == "__main__":
    asyncio.run(main())
