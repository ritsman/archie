
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

#DATABASE_URL = "postgresql+asyncpg://rits:tipra@localhost/archie"
DATABASE_URL="postgresql+asyncpg://rits:tipra@103.73.190.204:5432/archie"


engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)






