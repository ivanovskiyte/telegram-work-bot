import asyncio

from sqlalchemy import select

from database.db import async_session
from database.models import User
from services.excel_report import generate_monthly_report


async def main():
    telegram_id = 95456147

    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()

    if user is None:
        raise ValueError(
            f"Пользователь с telegram_id={telegram_id} не найден."
        )

    print(f"Пользователь найден: {user.name}")
    print(f"Внутренний ID: {user.id}")

    file_data, filename = await generate_monthly_report(
        user_id=user.id,
        year=2026,
        month=9,
    )

    with open(filename, "wb") as f:
        f.write(file_data.getvalue())

    print(f"Готово: {filename}")


if __name__ == "__main__":
    asyncio.run(main())