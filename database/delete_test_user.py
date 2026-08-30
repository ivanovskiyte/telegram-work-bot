import asyncio

from database.queries import delete_user_by_telegram_id


async def main():
    telegram_id = int(input("Введите Telegram ID пользователя для удаления: "))

    deleted = await delete_user_by_telegram_id(telegram_id)

    if deleted:
        print("Пользователь удалён")
    else:
        print("Пользователь не найден")


if __name__ == "__main__":
    asyncio.run(main())