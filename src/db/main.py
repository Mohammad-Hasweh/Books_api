from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from src.config import Config



async_engine = AsyncEngine(create_engine(url=Config.DATABASE_URL))




#Dependency injection in FastAPI allows for the sharing of state among multiple API routes by providing a mechanism to create Python objects,

async def init_db()-> None:
    """create our database model in the database"""

    async with async_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        #Note - conn.run_sync() is an asynchronous function that we utilize to run **synchronous** functions such as SQLModel.metadata.create_all().



async def get_session() -> AsyncSession:
    Session = sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with Session() as session:
        yield session