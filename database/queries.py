from sqlalchemy import select

from database.db import async_session
from database.models import User


async def get_user_by_telegram_id(telegram_id: int) -> User | None:
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()


async def create_user(
    telegram_id: int,
    name: str,
    role: str,
    fuel_consumption: float | None = None,
) -> User:
    async with async_session() as session:
        user = User(
            telegram_id=telegram_id,
            name=name,
            role=role,
            fuel_consumption=fuel_consumption,
        )

        session.add(user)
        await session.commit()
        await session.refresh(user)

        return user

async def delete_user_by_telegram_id(telegram_id: int) -> bool:
    async with async_session() as session:
        user = await get_user_by_telegram_id(telegram_id)

        if user is None:
            return False

        await session.delete(user)
        await session.commit()

        return True