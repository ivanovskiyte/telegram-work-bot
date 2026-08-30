from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from database.models import Base


DATABASE_URL = "sqlite+aiosqlite:///data/bot.db"

engine = create_async_engine(DATABASE_URL)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def create_tables():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)