from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Import your database tools
from app.db.database import get_db
from app.models.test_model import TestTable
from app.routers import interview

import logging
from fastapi import FastAPI
from app.routers import interview

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

# Example: Create a new record in your test_table
@app.post("/items/{name}")
async def create_item(name: str, db: AsyncSession = Depends(get_db)):
    new_item = TestTable(name=name)
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)
    return {"status": "created", "item": {"id": new_item.id, "name": new_item.name}}

# Example: Get all records from your test_table
@app.get("/items")
async def get_items(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TestTable))
    items = result.scalars().all()
    return items


app = FastAPI(title="Interview Question Generator")

app.include_router(interview.router)


@app.get("/health")
def health():
    return {"status": "ok"}
