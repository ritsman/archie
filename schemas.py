from pydantic import BaseModel
from datetime import date
from typing import List, Optional
#salesman class
#---------------------------------
class SalesmanBase(BaseModel):
    name: str
    commission: float | None = None
    phone: str | None = None

class SalesmanCreate(SalesmanBase):
    pass  # For creation, typically the same as base

class SalesmanResponse(SalesmanBase):
    id: int

    class Config:
        orm_mode = True  # This allows Pydantic to work with ORM objects

#---------------------------------
#client class

class ClientBase(BaseModel):
    name: str
    phone: str | None = None
    address: str | None = None

class ClientCreate(ClientBase):
    pass

class ClientResponse(ClientBase):
    id: int

    class Config:
        from_attributes = True   # Use this for Pydantic v2 and SQLAlchemy ORM output



class ProductBase(BaseModel):
    name: str
    weight: float | None = None
    rate: float | None = None

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int

    class Config:
        from_attributes = True  # Pydantic v2


class ClientMini(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class SalesmanMini(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

# For nested details in Slipdetail
class SlipDetailBase(BaseModel):
    product_id: int
    weight: Optional[float] = None
    quantity: int
    rate: float
    amount: float
    slip_date: date

class SlipDetailCreate(SlipDetailBase):
    pass

class SlipDetailResponse(SlipDetailBase):
    id: int
    product: Optional[ProductResponse]
    class Config:
        from_attributes = True
#slip main 
class SlipBase(BaseModel):
    slip_number: str
    client_id: int
    salesman_id: int
    slip_date: date
    vehicle_number: Optional[str] = None
    total_amount: float

class SlipCreate(SlipBase):
    slip_details: List[SlipDetailCreate]

class SlipResponse(SlipBase):
    id: int
    slip_details: List[SlipDetailResponse]
    client:ClientMini
    salesman: SalesmanMini

    class Config:
        from_attributes = True

#for row locking and number increment
class SlipSequenceBase(BaseModel):
    year2: str
    month2: str
    last_seq: int

class SlipSequenceResponse(SlipSequenceBase):
    class Config:
        from_attributes = True
