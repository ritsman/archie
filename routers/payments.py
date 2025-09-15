from fastapi import APIRouter, Depends, HTTPException,Query,Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import Payment,Clients
from schemas import PaymentCreate, PaymentResponse
from database import AsyncSessionLocal
from sqlalchemy.orm import selectinload


router = APIRouter(prefix="/payments", tags=["payments"])

async def get_session():
    async with AsyncSessionLocal() as session:
        yield session

# @router.post("/", response_model=PaymentResponse)
# async def create_payment(payment: PaymentCreate, session: AsyncSession = Depends(get_session)):
#     db_payment = Payment(**payment.model_dump())
#     session.add(db_payment)
#     await session.commit()
#     await session.refresh(db_payment)
    
#     # Eager load client relationship before returning
#     result = await session.execute(
#         select(Payment)
#         .options(selectinload(Payment.client))
#         .where(Payment.id == db_payment.id)
#     )
#     db_payment_with_client = result.scalar_one()
    
#     return db_payment_with_client

@router.post("/", response_model=PaymentResponse)
async def create_payment(payment: PaymentCreate, session: AsyncSession = Depends(get_session)):
    db_payment = Payment(**payment.model_dump())
    session.add(db_payment)
    await session.commit()
    await session.refresh(db_payment)

    # Eager load client
    result = await session.execute(
        select(Payment)
        .options(selectinload(Payment.client))
        .where(Payment.id == db_payment.id)
    )
    db_payment_with_client = result.scalar_one()
    return db_payment_with_client  # This ensures `client` is present

@router.get("/", response_model=list[PaymentResponse])
async def get_payments(
    limit: int = Query(100, ge=1, le=500),  # default 100, min 1, max 500
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(Payment)
        .options(selectinload(Payment.client))
        .order_by(Payment.id.desc())  # newest first if desired
        .limit(limit)
    )
    payments = result.scalars().all()
    return payments

@router.delete("/{payment_id}")
async def delete_payment(payment_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Payment).where(Payment.id == payment_id))
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    await session.delete(payment)
    await session.commit()
    return {"detail": "Payment deleted"}


@router.put("/{payment_id}", response_model=PaymentResponse)
async def update_payment(
    payment_id: int = Path(..., description="ID of the payment to update"),
    payment_update: PaymentCreate = None,   # or make a separate PaymentUpdate schema
    session: AsyncSession = Depends(get_session)
):
    # Fetch payment
    result = await session.execute(select(Payment).where(Payment.id == payment_id))
    db_payment = result.scalar_one_or_none()

    if not db_payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    # Update only fields provided
    update_data = payment_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_payment, key, value)

    await session.commit()
    await session.refresh(db_payment)

    # Eager load client for response
    result = await session.execute(
        select(Payment)
        .options(selectinload(Payment.client))
        .where(Payment.id == db_payment.id)
    )
    updated_payment = result.scalar_one()

    return updated_payment
