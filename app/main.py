from dotenv import load_dotenv
load_dotenv('.env_dbf2ee37-0d53-416c-8916-7748075b87f8', override=True)

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine

from app.database import Base, engine
from app.routers import auth, customers, addresses, contacts, notes, activities, audit_logs

app = FastAPI(title="Customer Management System API", version="1.0.0")


@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(customers.router)
app.include_router(addresses.router)
app.include_router(contacts.router)
app.include_router(notes.router)
app.include_router(activities.router)
app.include_router(audit_logs.router)
