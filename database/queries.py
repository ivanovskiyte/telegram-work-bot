from sqlalchemy import select


from database.db import async_session
from database.models import User, MileageSetting


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

async def get_all_users() -> list[User]:
    async with async_session() as session:
        result = await session.execute(
            select(User).order_by(User.id)
        )
        return list(result.scalars().all())


async def update_user_role(
    telegram_id: int,
    role: str,
    fuel_consumption: float | None,
) -> User | None:
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()

        if user is None:
            return None

        user.role = role
        user.fuel_consumption = fuel_consumption

        await session.commit()
        await session.refresh(user)

        return user

async def create_mileage_setting(
    workplace: str,
    mileage: float,
) -> MileageSetting:
    async with async_session() as session:
        setting = MileageSetting(
            workplace=workplace,
            mileage=mileage,
        )

        session.add(setting)
        await session.commit()
        await session.refresh(setting)

        return setting


async def get_all_mileage_settings() -> list[MileageSetting]:
    async with async_session() as session:
        result = await session.execute(
            select(MileageSetting).order_by(MileageSetting.id)
        )
        return list(result.scalars().all())


async def get_mileage_setting(
    workplace: str,
) -> MileageSetting | None:
    async with async_session() as session:
        result = await session.execute(
            select(MileageSetting)
        )
        settings = result.scalars().all()

        workplace_normalized = workplace.strip().casefold()

        for setting in settings:
            if setting.workplace.strip().casefold() == workplace_normalized:
                return setting

        return None


async def delete_mileage_setting(
    workplace: str,
) -> bool:
    async with async_session() as session:
        result = await session.execute(
            select(MileageSetting)
        )
        settings = result.scalars().all()

        workplace_normalized = workplace.strip().casefold()

        for setting in settings:
            if setting.workplace.strip().casefold() == workplace_normalized:
                await session.delete(setting)
                await session.commit()
                return True

        return False