from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import Clients
from schemas import ClientCreate, ClientResponse
from database import AsyncSessionLocal  # adjust as per your code

router = APIRouter(prefix="/clients", tags=["clients"])

# Dependency
async def get_session():
    async with AsyncSessionLocal() as session:
        yield session

# CREATE
@router.post("/", response_model=ClientResponse)
async def create_client(client: ClientCreate, session: AsyncSession = Depends(get_session)):
    db_client = Clients(**client.model_dump())  # For Pydantic v2+
    session.add(db_client)
    await session.commit()
    await session.refresh(db_client)
    return db_client

# READ ALL
@router.get("/", response_model=list[ClientResponse])
async def get_clients(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Clients))
    return result.scalars().all()

# READ ONE
@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(client_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Clients).filter(Clients.id == client_id))
    client = result.scalars().first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

# UPDATE
@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: int,
    client_update: ClientCreate,
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(select(Clients).filter(Clients.id == client_id))
    db_client = result.scalars().first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    db_client.name = client_update.name
    db_client.phone = client_update.phone
    db_client.address = client_update.address
    await session.commit()
    await session.refresh(db_client)
    return db_client

# DELETE
@router.delete("/{client_id}")
async def delete_client(client_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Clients).filter(Clients.id == client_id))
    db_client = result.scalars().first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    await session.delete(db_client)
    await session.commit()
    return {"detail": "Client deleted successfully"}
