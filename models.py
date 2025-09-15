from sqlalchemy import Column, Integer, String, Float,Column, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base
import datetime
#from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
#from sqlalchemy.orm import relationship
#from .database import Base

Base = declarative_base()

class Salesman(Base):
    __tablename__ = "salesman"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    commission = Column(Float, nullable=True)
    phone = Column(String, nullable=True,unique=True)

class Clients(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True, unique=True)
    address = Column(String, nullable=True)

    def __repr__(self):
        return f"<Client(name={self.name}, phone={self.phone}, address={self.address})>"
    
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    weight = Column(Float, nullable=True)
    rate = Column(Float, nullable=True)
    



class Slip(Base):
    __tablename__ = "slips"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    slip_number = Column(String, unique=True, nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    salesman_id = Column(Integer, ForeignKey("salesman.id"), nullable=False)
    slip_date = Column(Date, nullable=False)
    vehicle_number = Column(String, nullable=True)
    total_amount = Column(Float, nullable=False)
    slip_details = relationship("SlipDetail", back_populates="slip", cascade="all, delete-orphan")
    client = relationship("Clients")
    salesman = relationship("Salesman")

class SlipDetail(Base):
    __tablename__ = "slip_details"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    slip_id = Column(Integer, ForeignKey("slips.id"), nullable=False, index=True)  # FK to slips
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    weight = Column(Float, nullable=True)
    quantity = Column(Integer, nullable=False)
    rate = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)
    slip_date = Column(Date, nullable=False)  # typically same as Slip.slip_date but stored here too

    # Relationships to access linked data
    slip = relationship("Slip", back_populates="slip_details")
    product = relationship("Product")


class SlipSequence(Base):
    __tablename__ = "slip_sequences"

    year2 = Column(String(2), primary_key=True)
    month2 = Column(String(2), primary_key=True)
    last_seq = Column(Integer, nullable=False)




class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    notes = Column(String, nullable=True)
    date = Column(Date, default=datetime.date.today, nullable=False)

    client = relationship("Clients")  # Optional, for ORM navigation if needed
