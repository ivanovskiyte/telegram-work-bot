from sqlalchemy import select
from datetime import date

from database.db import async_session
from database.models import User, MileageSetting, DailyReport, FuelBatch, FuelConsumptionAllocation


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

async def consume_fuel_fifo(
    session,
    user_id: int,
    daily_report_id: int,
    fuel_consumed: float,
) -> None:
    if fuel_consumed <= 0:
        return

    result = await session.execute(
        select(FuelBatch)
        .where(
            FuelBatch.user_id == user_id,
            FuelBatch.remaining_liters > 0,
        )
        .order_by(FuelBatch.id)
    )
    batches = result.scalars().all()

    remaining_to_consume = fuel_consumed

    for batch in batches:
        if remaining_to_consume <= 0:
            break

        consumed_from_batch = min(
            batch.remaining_liters,
            remaining_to_consume,
        )

        cost = round(
            consumed_from_batch * batch.price_per_liter,
            2,
        )

        batch.remaining_liters -= consumed_from_batch

        allocation = FuelConsumptionAllocation(
            daily_report_id=daily_report_id,
            fuel_batch_id=batch.id,
            liters=consumed_from_batch,
            cost=cost,
        )

        session.add(allocation)

        remaining_to_consume -= consumed_from_batch

async def create_daily_report(
    user_id: int,
    report_date: date,
    workplace: str,
    mileage: float,
    refueled: bool,
    fuel_liters: float | None,
    fuel_amount: float | None,
    work_description: str,
    work_completed: bool,
    is_out_of_town: bool,
) -> DailyReport:
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if user is None:
            raise ValueError(f"User with id {user_id} not found")

        fuel_consumption_rate = user.fuel_consumption

        if is_out_of_town and fuel_consumption_rate is not None:
            fuel_consumed = mileage * fuel_consumption_rate / 100
        else:
            fuel_consumed = 0.0

        report = DailyReport(
            user_id=user_id,
            report_date=report_date,
            workplace=workplace,
            mileage=mileage,
            refueled=refueled,
            fuel_liters=fuel_liters,
            fuel_amount=fuel_amount,
            work_description=work_description,
            work_completed=work_completed,
            is_out_of_town=is_out_of_town,
            fuel_consumption_rate=fuel_consumption_rate,
            fuel_consumed=fuel_consumed,
        )

        session.add(report)
        await session.flush()

        if refueled and fuel_liters is not None and fuel_amount is not None:
            price_per_liter = round(fuel_amount / fuel_liters, 2)

            fuel_batch = FuelBatch(
                user_id=user_id,
                daily_report_id=report.id,
                liters=fuel_liters,
                amount=fuel_amount,
                price_per_liter=price_per_liter,
                remaining_liters=fuel_liters,
            )

            session.add(fuel_batch)
            await session.flush()

        if fuel_consumed > 0:
            await consume_fuel_fifo(
                session=session,
                user_id=user_id,
                daily_report_id=report.id,
                fuel_consumed=fuel_consumed,
            )
        

        await session.commit()
        await session.refresh(report)

        return report