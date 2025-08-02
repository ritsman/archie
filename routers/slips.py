
import json
from fastapi import APIRouter, Depends,Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from models import Slip, SlipDetail, SlipSequence
from schemas import SlipCreate, SlipResponse
from database import AsyncSessionLocal
from sqlalchemy import select, func
from datetime import datetime
from sqlalchemy.future import select
from sqlalchemy import distinct
from sqlalchemy.orm import selectinload


router = APIRouter(prefix="/slips", tags=["slips"])

async def get_session():
    async with AsyncSessionLocal() as session:
        yield session
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

async def get_next_slip_number(session: AsyncSession, slip_date):
    year2 = slip_date.strftime("%y")
    month2 = slip_date.strftime("%m")
    # Lock the row for this (year2, month2), or create it if not exists.
    # Start a subtransaction for safety
    result = await session.execute(
        select(SlipSequence).where(
            SlipSequence.year2 == year2,
            SlipSequence.month2 == month2
        ).with_for_update()
    )
    seq_row = result.scalar_one_or_none()

    if seq_row is None:
        seq_row = SlipSequence(year2=year2, month2=month2, last_seq=1)
        session.add(seq_row)
        seq_num = 1
    else:
        seq_row.last_seq += 1
        seq_num = seq_row.last_seq

    slip_number = f"{year2}{month2}{str(seq_num).zfill(3)}"
    return slip_number

@router.post("/ee", response_model=SlipResponse)
async def create_slip(slip: SlipCreate, session: AsyncSession = Depends(get_session)):
    #logging.info(f"Received slip data: {slip}")
    print(slip)
    async with session.begin():  # ensures this block is a transaction
        slip_number = await get_next_slip_number(session, slip.slip_date)
        db_slip = Slip(
            slip_number=slip_number,
            client_id=slip.client_id,
            salesman_id=slip.salesman_id,
            slip_date=slip.slip_date,
            vehicle_number=slip.vehicle_number,
            total_amount=slip.total_amount
        )
        session.add(db_slip)
        await session.flush()  # ensures db_slip.id is assigned

        # Add slip_details
        for detail in slip.slip_details:
            db_detail = SlipDetail(
                slip_id=db_slip.id,
                product_id=detail.product_id,
                weight=detail.weight,
                quantity=detail.quantity,
                rate=detail.rate,
                amount=detail.amount,
                slip_date=detail.slip_date
            )
            session.add(db_detail)

    # No need to await session.commit() after session.begin(): block, it auto-commits on success.
    await session.refresh(db_slip)
    return db_slip

@router.post("/", response_model=SlipResponse)
async def create_slip(slip: SlipCreate, session: AsyncSession = Depends(get_session)):
    async with session.begin():
        slip_number = await get_next_slip_number(session, slip.slip_date)
        db_slip = Slip(
            slip_number=slip_number,
            client_id=slip.client_id,
            salesman_id=slip.salesman_id,
            slip_date=slip.slip_date,
            vehicle_number=slip.vehicle_number,
            total_amount=slip.total_amount
        )
        session.add(db_slip)
        await session.flush()

        for detail in slip.slip_details:
            db_detail = SlipDetail(
                slip_id=db_slip.id,
                product_id=detail.product_id,
                weight=detail.weight,
                quantity=detail.quantity,
                rate=detail.rate,
                amount=detail.amount,
                slip_date=detail.slip_date
            )
            session.add(db_detail)

    await session.commit()

    # Eager load slip_details to avoid lazy loading issues
    result = await session.execute(
        select(Slip).options(selectinload(Slip.slip_details)).filter(Slip.id == db_slip.id)
    )
    slip_with_details = result.scalar_one()

    return slip_with_details




@router.get("/generate_slip_number")
async def generate_slip_number(
    date: str = Query(..., description="Date in ISO format (YYYY-MM-DD)"),
    session: AsyncSession = Depends(get_session)
):
    """
    Returns the next available slip number for a given date.
    This does NOT increment any sequence or save anything.
    """
    # Parse date string to datetime/date object
    try:
        slip_date = datetime.fromisoformat(date).date()
    except Exception:
        return "Invalid date format", 400

    year_str = slip_date.strftime("%y")  # last 2 digits of year
    month_str = slip_date.strftime("%m") # 2-digit month

    # Pattern to match slip_numbers starting with year+month
    like_pattern = f"{year_str}{month_str}%"

    # Query the highest slip number in this year/month
    result = await session.execute(
        select(func.max(Slip.slip_number)).where(Slip.slip_number.like(like_pattern))
    )
    max_slip_number = result.scalar_one_or_none()

    if max_slip_number:
        seq = int(max_slip_number[-3:]) + 1  # increment sequence
    else:
        seq = 1

    slip_number = f"{year_str}{month_str}{str(seq).zfill(3)}"
    return slip_number





@router.get("/vehicle_numbers/", response_model=list[str])
async def get_vehicle_numbers(session: AsyncSession = Depends(get_session)):
    """
    Returns a list of distinct vehicle numbers used in previously saved slips.
    Excludes null or empty strings.
    """
    result = await session.execute(
        select(distinct(Slip.vehicle_number))
        .where(Slip.vehicle_number.isnot(None))
        .where(Slip.vehicle_number != "")
    )
    vehicle_numbers = [row[0] for row in result.all()]
    return vehicle_numbers

@router.get("/", response_model=list[SlipResponse])
async def get_slips(session: AsyncSession = Depends(get_session)):
    """
    Returns all slips with their slip details (eager loaded).
    """
    result = await session.execute(
        select(Slip).options(
            selectinload(Slip.client),
            selectinload(Slip.salesman),
            selectinload(Slip.slip_details).selectinload(SlipDetail.product))  # Eager load slip_details
    )
    slips = result.scalars().unique().all()
    # for slip in slips:
    #     slip_dict = {
    #         "id": slip.id,
    #         "slip_number": slip.slip_number,
    #         "slip_details": [
    #             {
    #                 "id": detail.id,
    #                 "product_id": detail.product_id,
    #                 "product_name": detail.product.name if detail.product else None,
    #                 "quantity": detail.quantity,
    #                 "rate": detail.rate,
    #                 "amount": detail.amount,
    #             }
    #             for detail in slip.slip_details
    #         ],
    #     }
    #     print(json.dumps(slip_dict, indent=2))
    return slips