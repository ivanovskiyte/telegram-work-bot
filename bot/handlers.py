from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext


from database.queries import get_user_by_telegram_id, create_user
from bot.states import RegistrationStates


router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user = await get_user_by_telegram_id(message.from_user.id)

    if user is None:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Оператор"),
                    KeyboardButton(text="Просмотр"),
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )

        await message.answer(
            "Вы не зарегистрированы в системе.\n"
            "Выберите тип учётной записи:",
            reply_markup=keyboard,
        )

        await state.set_state(RegistrationStates.choosing_role)
        return

    await message.answer(
        f"Привет, {user.name}!\n"
        f"Ваша роль: {user.role}"
    )




@router.message(RegistrationStates.choosing_role)
async def process_role_choice(message: Message, state: FSMContext):
    if message.text == "Просмотр":
        user = await create_user(
            telegram_id=message.from_user.id,
            name=message.from_user.full_name,
            role="viewer",
            fuel_consumption=None,
        )

        await message.answer(
            f"Регистрация завершена.\n"
            f"Имя: {user.name}\n"
            f"Роль: {user.role}"
        )


        await state.clear()
        return

    if message.text == "Оператор":
        await message.answer(
            "Вы выбрали тип учётной записи: Оператор.\n"
            "Введите ваш расход топлива в л/100 км:"
        )

        await state.set_state(
            RegistrationStates.entering_fuel_consumption
        )
        return

    await message.answer(
        "Пожалуйста, выберите один из вариантов кнопками."
    )    




@router.message(RegistrationStates.entering_fuel_consumption)
async def process_fuel_consumption(message: Message, state: FSMContext):
    try:
        fuel_consumption = float(message.text.replace(",", "."))
    except (ValueError, AttributeError):
        await message.answer(
            "Введите расход числом, например: 6.5"
        )
        return

    if fuel_consumption <= 0:
        await message.answer(
            "Расход должен быть больше нуля. Попробуйте ещё раз."
        )
        return

    user = await create_user(
        telegram_id=message.from_user.id,
        name=message.from_user.full_name,
        role="operator",
        fuel_consumption=fuel_consumption,
    )

    await message.answer(
        f"Регистрация завершена.\n"
        f"Имя: {user.name}\n"
        f"Роль: {user.role}\n"
        f"Расход: {user.fuel_consumption} л/100 км."
    )



    await state.clear()