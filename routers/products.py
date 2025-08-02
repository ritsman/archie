from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import Product
from schemas import ProductCreate, ProductResponse
from database import AsyncSessionLocal

router = APIRouter(prefix="/products", tags=["products"])

async def get_session():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/", response_model=ProductResponse)
async def create_product(product: ProductCreate, session: AsyncSession = Depends(get_session)):
    db_product = Product(**product.model_dump())
    session.add(db_product)
    await session.commit()
    await session.refresh(db_product)
    return db_product

@router.get("/", response_model=list[ProductResponse])
async def get_products(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Product))
    return result.scalars().all()

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Product).filter(Product.id == product_id))
    product = result.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: int, product_update: ProductCreate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Product).filter(Product.id == product_id))
    db_product = result.scalars().first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    db_product.name = product_update.name
    db_product.weight = product_update.weight
    db_product.rate = product_update.rate
    await session.commit()
    await session.refresh(db_product)
    return db_product

@router.delete("/{product_id}")
async def delete_product(product_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Product).filter(Product.id == product_id))
    db_product = result.scalars().first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    await session.delete(db_product)
    await session.commit()
    return {"detail": "Product deleted successfully"}
