from fastapi import FastAPI, Depends, HTTPException,Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import Base, Salesman
from schemas import SalesmanCreate, SalesmanResponse
from database import AsyncSessionLocal, engine
from contextlib import asynccontextmanager

from fastapi.middleware.cors import CORSMiddleware
from routers import clients_router,products_router,slips_router # Importing the clients router




@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield  # Application runs here
    # Shutdown code (optional)
    # (e.g., close connections or cleanup)

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend addresses
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Dependency
async def get_session():
    async with AsyncSessionLocal() as session:
        yield session

@app.post("/salesmen/", response_model=SalesmanResponse)
async def create_salesman(salesman: SalesmanCreate, session: AsyncSession = Depends(get_session)):
    if salesman.phone:
        result = await session.execute(select(Salesman).filter(Salesman.phone == salesman.phone))
        existing_salesman = result.scalars().first()

        if existing_salesman:
            # Update existing record
            existing_salesman.name = salesman.name
            existing_salesman.commission = salesman.commission
            # phone stays the same since it is unique and matched
            await session.commit()
            await session.refresh(existing_salesman)
            return existing_salesman

    # If no existing salesman with this phone, create new
    db_salesman = Salesman(**salesman.model_dump())
    session.add(db_salesman)
    await session.commit()
    await session.refresh(db_salesman)
    return db_salesman

@app.get("/salesmen/", response_model=list[SalesmanResponse])
async def get_salesmen(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Salesman))
    return result.scalars().all()

@app.put("/salesmen/{salesman_id}", response_model=SalesmanResponse)
async def update_salesman(
    salesman_update: SalesmanCreate,
    salesman_id: int = Path(..., title="The ID of the salesman to update"),
    
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(Salesman).filter(Salesman.id == salesman_id))
    db_salesman = result.scalars().first()
    if not db_salesman:
        raise HTTPException(status_code=404, detail="Salesman not found")
    
    db_salesman.name = salesman_update.name
    db_salesman.commission = salesman_update.commission
    db_salesman.phone = salesman_update.phone
    await session.commit()
    await session.refresh(db_salesman)
    return db_salesman


@app.delete("/salesmen/{salesman_id}")
async def delete_salesman(
    salesman_id: int = Path(..., title="The ID of the salesman to delete"),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(Salesman).filter(Salesman.id == salesman_id))
    db_salesman = result.scalars().first()
    if not db_salesman:
        raise HTTPException(status_code=404, detail="Salesman not found")
    
    await session.delete(db_salesman)
    await session.commit()
    return {"detail": "Salesman deleted successfully"}

app.include_router(clients_router)  # Include the clients router
app.include_router(products_router)  # Include the clients router
app.include_router(slips_router)  # Include the clients router
