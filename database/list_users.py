from sqlalchemy import select

from database.db import async_session
from database.models import User


async def main():
    async with async_session() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()

        if not users:
            print("Пользователей в базе нет")
            return

        for user in users:
            print(f"ID: {user.id}")
            print(f"Telegram ID: {user.telegram_id}")
            print(f"Имя: {user.name}")
            print(f"Роль: {user.role}")
            print(f"Расход: {user.fuel_consumption}")
            print("-" * 30)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())