from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from database.queries import get_user_by_telegram_id

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    user = await get_user_by_telegram_id(message.from_user.id)

    if user is None:
        await message.answer(
            "Вы не зарегистрированы в системе."
        )
        return

    await message.answer(
        f"Привет, {user.name}!\n"
        f"Ваша роль: {user.role}"
    )