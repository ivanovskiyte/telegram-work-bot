from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from database.queries import (
    get_user_by_telegram_id,
    create_user,
    get_all_users,
    delete_user_by_telegram_id,
    update_user_role,
    create_mileage_setting,
    get_mileage_setting,
    get_all_mileage_settings,
    delete_mileage_setting,
)
from bot.states import RegistrationStates, AdminStates
from bot.keyboards import (
    admin_keyboard,
    operator_keyboard,
    viewer_keyboard,
    additional_keyboard,
    admin_section_keyboard,
    user_management_keyboard,
    manual_input_keyboard,
    notification_settings_keyboard,
    mileage_settings_keyboard,
)


router = Router()


# =========================
# /start
# =========================

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user = await get_user_by_telegram_id(message.from_user.id)

    if user is None:
        from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Инженер"),
                    KeyboardButton(text="Офис"),
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

    await show_main_menu(message, user)





# =========================
# Главное меню по роли
# =========================

async def show_main_menu(message: Message, user):
    if user.role == "administrator":
        await message.answer(
            f"Привет, {user.name}!\n"
            "Главное меню:",
            reply_markup=admin_keyboard(),
        )

    elif user.role == "operator":
        await message.answer(
            f"Привет, {user.name}!\n"
            "Главное меню:",
            reply_markup=operator_keyboard(),
        )

    elif user.role == "viewer":
        await message.answer(
            f"Привет, {user.name}!\n"
            "Главное меню:",
            reply_markup=viewer_keyboard(),
        )






# =========================
# Регистрация
# =========================

@router.message(RegistrationStates.choosing_role)
async def process_role_choice(message: Message, state: FSMContext):
    if message.text == "Офис":
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
        await show_main_menu(message, user)
        return

    if message.text == "Инженер":
        await message.answer(
            "Вы выбрали тип учётной записи: Инженер.\n"
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
    await show_main_menu(message, user)






# =========================
# АДМИНИСТРАТОР
# =========================

@router.message(lambda message: message.text == "Дополнительно")
async def admin_additional(message: Message):
    user = await get_user_by_telegram_id(message.from_user.id)

    if user is None or user.role != "administrator":
        return

    await message.answer(
        "Дополнительно:",
        reply_markup=additional_keyboard(),
    )

@router.message(lambda message: message.text == "Администратор")
async def admin_section(message: Message):
    user = await get_user_by_telegram_id(message.from_user.id)

    if user is None or user.role != "administrator":
        return

    await message.answer(
        "Раздел администратора:",
        reply_markup=admin_section_keyboard(),
    )

@router.message(lambda message: message.text == "Управление пользователями")
async def user_management(message: Message):
    user = await get_user_by_telegram_id(message.from_user.id)

    if user is None or user.role != "administrator":
        return

    await message.answer(
        "Управление пользователями:",
        reply_markup=user_management_keyboard(),
    )






# =========================
# Просмотр пользователей
# =========================

@router.message(lambda message: message.text == "Просмотр пользователей")
async def view_users(message: Message):
    user = await get_user_by_telegram_id(message.from_user.id)

    if user is None or user.role != "administrator":
        return

    users = await get_all_users()

    if not users:
        await message.answer("Пользователей в базе нет.")
        return

    text = ""

    for item in users:
        text += (
            f"ID: {item.id}\n"
            f"Telegram ID: {item.telegram_id}\n"
            f"Имя: {item.name}\n"
            f"Роль: {item.role}\n"
            f"Расход: {item.fuel_consumption}\n\n"
        )

    await message.answer(text)





# =========================
# Удаление пользователей
# =========================

@router.message(lambda message: message.text == "Удаление пользователя")
async def delete_user_start(message: Message, state: FSMContext):
    user = await get_user_by_telegram_id(message.from_user.id)

    if user is None or user.role != "administrator":
        return

    await message.answer(
        "Введите Telegram ID пользователя, которого нужно удалить:"
    )

    await state.set_state(AdminStates.deleting_user)

@router.message(AdminStates.deleting_user)
async def delete_user_get_id(message: Message, state: FSMContext):
    try:
        telegram_id = int(message.text)
    except (ValueError, TypeError):
        await state.clear()

        await message.answer(
            "Некорректный Telegram ID.\n"
            "Операция удаления отменена.",
            reply_markup=user_management_keyboard(),
        )
        return

    user = await get_user_by_telegram_id(telegram_id)

    if user is None:
        await state.clear()

        await message.answer(
            "Пользователь с таким Telegram ID не найден.\n"
            "Операция удаления отменена.",
            reply_markup=user_management_keyboard(),
        )
        return

    await state.update_data(delete_telegram_id=telegram_id)

    await message.answer(
        f"Пользователь найден:\n\n"
        f"ID: {user.id}\n"
        f"Telegram ID: {user.telegram_id}\n"
        f"Имя: {user.name}\n"
        f"Роль: {user.role}\n\n"
        "Удалить этого пользователя?\n"
        "Ответьте «Да» или «Нет»."
    )

    await state.set_state(AdminStates.confirming_deletion)

@router.message(AdminStates.confirming_deletion)
async def delete_user_confirm(message: Message, state: FSMContext):
    if message.text not in ("Да", "Нет"):
        await message.answer(
            "Пожалуйста, ответьте «Да» или «Нет»."
        )
        return

    if message.text == "Нет":
        await message.answer("Удаление отменено.")
        await state.clear()
        return

    data = await state.get_data()
    telegram_id = data.get("delete_telegram_id")

    deleted = await delete_user_by_telegram_id(telegram_id)

    if deleted:
        await message.answer("Пользователь удалён.")
    else:
        await message.answer(
            "Не удалось удалить пользователя. "
            "Возможно, он уже отсутствует в базе."
        )

    await state.clear()




# =========================
# Смена роли пользователя
# =========================

@router.message(lambda message: message.text == "Смена роли пользователя")
async def change_role_start(message: Message, state: FSMContext):
    user = await get_user_by_telegram_id(message.from_user.id)

    if user is None or user.role != "administrator":
        return

    await message.answer(
        "Введите Telegram ID пользователя, которому нужно изменить роль:"
    )

    await state.set_state(AdminStates.changing_role)

@router.message(AdminStates.changing_role)
async def change_role_get_id(message: Message, state: FSMContext):
    try:
        telegram_id = int(message.text)
    except (ValueError, TypeError):
        await state.clear()

        await message.answer(
            "Некорректный Telegram ID.\n"
            "Операция смены роли отменена.",
            reply_markup=user_management_keyboard(),
        )
        return

    user = await get_user_by_telegram_id(telegram_id)

    if user is None:
        await state.clear()

        await message.answer(
            "Пользователь с таким Telegram ID не найден.\n"
            "Операция смены роли отменена.",
            reply_markup=user_management_keyboard(),
        )
        return

    await state.update_data(change_role_telegram_id=telegram_id)

    await message.answer(
        f"Пользователь найден:\n\n"
        f"ID: {user.id}\n"
        f"Telegram ID: {user.telegram_id}\n"
        f"Имя: {user.name}\n"
        f"Роль: {user.role}\n"
        f"Расход: {user.fuel_consumption}\n\n"
        "Выберите новую роль:\n"
        "Инженер или Офис"
    )

    await state.set_state(AdminStates.selecting_new_role)

@router.message(AdminStates.selecting_new_role)
async def change_role_select(message: Message, state: FSMContext):
    if message.text not in ("Инженер", "Офис"):
        await state.clear()

        await message.answer(
            "Некорректный выбор.\n"
            "Операция смены роли отменена.",
            reply_markup=user_management_keyboard(),
        )
        return

    new_role = "operator" if message.text == "Инженер" else "viewer"

    await state.update_data(new_role=new_role)

    if new_role == "operator":
        await message.answer(
            "Введите новый расход топлива в л/100 км:"
        )

        await state.set_state(
            AdminStates.entering_new_fuel_consumption
        )
        return

    await state.update_data(new_fuel_consumption=None)

    await message.answer(
        "Новая роль: Офис\n"
        "Расход: не используется.\n\n"
        "Подтвердить изменение?\n"
        "Ответьте «Да» или «Нет»."
    )

    await state.set_state(AdminStates.confirming_role_change)

@router.message(AdminStates.entering_new_fuel_consumption)
async def change_role_fuel_consumption(
    message: Message,
    state: FSMContext,
):
    try:
        fuel_consumption = float(message.text.replace(",", "."))
    except (ValueError, AttributeError):
        await state.clear()

        await message.answer(
            "Некорректный расход.\n"
            "Операция смены роли отменена.",
            reply_markup=user_management_keyboard(),
        )
        return

    if fuel_consumption <= 0:
        await state.clear()

        await message.answer(
            "Расход должен быть больше нуля.\n"
            "Операция смены роли отменена.",
            reply_markup=user_management_keyboard(),
        )
        return

    await state.update_data(
        new_fuel_consumption=fuel_consumption
    )

    await message.answer(
        f"Новая роль: Инженер\n"
        f"Новый расход: {fuel_consumption} л/100 км.\n\n"
        "Подтвердить изменение?\n"
        "Ответьте «Да» или «Нет»."
    )

    await state.set_state(AdminStates.confirming_role_change)

@router.message(AdminStates.confirming_role_change)
async def change_role_confirm(
    message: Message,
    state: FSMContext,
):
    if message.text not in ("Да", "Нет"):
        await state.clear()

        await message.answer(
            "Некорректный ответ.\n"
            "Операция смены роли отменена.",
            reply_markup=user_management_keyboard(),
        )
        return

    if message.text == "Нет":
        await state.clear()

        await message.answer(
            "Изменение роли отменено.",
            reply_markup=user_management_keyboard(),
        )
        return

    data = await state.get_data()

    telegram_id = data.get("change_role_telegram_id")
    new_role = data.get("new_role")
    new_fuel_consumption = data.get("new_fuel_consumption")

    user = await update_user_role(
        telegram_id=telegram_id,
        role=new_role,
        fuel_consumption=new_fuel_consumption,
    )

    await state.clear()

    if user is None:
        await message.answer(
            "Не удалось изменить роль пользователя.",
            reply_markup=user_management_keyboard(),
        )
        return

    await message.answer(
        f"Роль пользователя изменена.\n\n"
        f"ID: {user.id}\n"
        f"Telegram ID: {user.telegram_id}\n"
        f"Имя: {user.name}\n"
        f"Роль: {user.role}\n"
        f"Расход: {user.fuel_consumption}",
        reply_markup=user_management_keyboard(),
    )




# =========================
# Настройка километражей
# =========================

@router.message(lambda message: message.text == "Настройка километражей")
async def mileage_settings(message: Message):
    user = await get_user_by_telegram_id(message.from_user.id)

    if user is None or user.role != "administrator":
        return

    await message.answer(
        "Настройка километражей:",
        reply_markup=mileage_settings_keyboard(),
    )


# Добавление

@router.message(lambda message: message.text == "Добавить")
async def add_mileage_start(message: Message, state: FSMContext):
    user = await get_user_by_telegram_id(message.from_user.id)

    if user is None or user.role != "administrator":
        return

    await message.answer(
        "Введите место работы:"
    )

    await state.set_state(
        AdminStates.adding_mileage_workplace
    )

@router.message(AdminStates.adding_mileage_workplace)
async def add_mileage_get_workplace(
    message: Message,
    state: FSMContext,
):
    workplace = message.text.strip()

    if not workplace:
        await state.clear()

        await message.answer(
            "Место работы не может быть пустым.\n"
            "Операция отменена.",
            reply_markup=mileage_settings_keyboard(),
        )
        return

    existing = await get_mileage_setting(workplace)

    if existing is not None:
        await state.clear()

        await message.answer(
            "Такое место уже есть в настройках.\n"
            "Операция добавления отменена.",
            reply_markup=mileage_settings_keyboard(),
        )
        return

    await state.update_data(
        mileage_workplace=workplace
    )

    await message.answer(
        "Введите километраж:"
    )

    await state.set_state(
        AdminStates.adding_mileage_value
    )

@router.message(AdminStates.adding_mileage_value)
async def add_mileage_get_value(
    message: Message,
    state: FSMContext,
):
    try:
        mileage = float(message.text.replace(",", "."))
    except (ValueError, AttributeError):
        await state.clear()

        await message.answer(
            "Километраж должен быть числом.\n"
            "Операция добавления отменена.",
            reply_markup=mileage_settings_keyboard(),
        )
        return

    if mileage <= 0:
        await state.clear()

        await message.answer(
            "Километраж должен быть больше нуля.\n"
            "Операция добавления отменена.",
            reply_markup=mileage_settings_keyboard(),
        )
        return

    data = await state.get_data()
    workplace = data["mileage_workplace"]

    setting = await create_mileage_setting(
        workplace=workplace,
        mileage=mileage,
    )

    await state.clear()

    await message.answer(
        f"Настройка добавлена.\n\n"
        f"Место: {setting.workplace}\n"
        f"Километраж: {setting.mileage}",
        reply_markup=mileage_settings_keyboard(),
    )


# Просмотр

@router.message(lambda message: message.text == "Просмотреть")
async def view_mileage_settings(message: Message):
    user = await get_user_by_telegram_id(message.from_user.id)

    if user is None or user.role != "administrator":
        return

    settings = await get_all_mileage_settings()

    if not settings:
        await message.answer(
            "Настроек километражей пока нет.",
            reply_markup=mileage_settings_keyboard(),
        )
        return

    text = "Настройки километражей:\n\n"

    for setting in settings:
        text += (
            f"ID: {setting.id}\n"
            f"Место: {setting.workplace}\n"
            f"Километраж: {setting.mileage}\n\n"
        )

    await message.answer(
        text,
        reply_markup=mileage_settings_keyboard(),
    )


# Удаление

@router.message(lambda message: message.text == "Удалить")
async def delete_mileage_start(message: Message, state: FSMContext):
    user = await get_user_by_telegram_id(message.from_user.id)

    if user is None or user.role != "administrator":
        return

    await message.answer(
        "Введите место работы, которое нужно удалить:"
    )

    await state.set_state(
        AdminStates.deleting_mileage
    )

@router.message(AdminStates.deleting_mileage)
async def delete_mileage_get_workplace(
    message: Message,
    state: FSMContext,
):
    workplace = message.text.strip()

    if not workplace:
        await state.clear()

        await message.answer(
            "Место работы не может быть пустым.\n"
            "Операция удаления отменена.",
            reply_markup=mileage_settings_keyboard(),
        )
        return

    setting = await get_mileage_setting(workplace)

    if setting is None:
        await state.clear()

        await message.answer(
            "Такое место не найдено.\n"
            "Операция удаления отменена.",
            reply_markup=mileage_settings_keyboard(),
        )
        return

    await state.update_data(
        mileage_delete_workplace=setting.workplace
    )

    await message.answer(
        f"Найдена настройка:\n\n"
        f"Место: {setting.workplace}\n"
        f"Километраж: {setting.mileage}\n\n"
        "Удалить эту настройку?\n"
        "Ответьте «Да» или «Нет»."
    )

    await state.set_state(
        AdminStates.confirming_mileage_deletion
    )

@router.message(AdminStates.confirming_mileage_deletion)
async def delete_mileage_confirm(
    message: Message,
    state: FSMContext,
):
    if message.text not in ("Да", "Нет"):
        await state.clear()

        await message.answer(
            "Некорректный ответ.\n"
            "Операция удаления отменена.",
            reply_markup=mileage_settings_keyboard(),
        )
        return

    if message.text == "Нет":
        await state.clear()

        await message.answer(
            "Удаление отменено.",
            reply_markup=mileage_settings_keyboard(),
        )
        return

    data = await state.get_data()

    workplace = data.get("mileage_delete_workplace")

    deleted = await delete_mileage_setting(workplace)

    await state.clear()

    if deleted:
        await message.answer(
            "Настройка километража удалена.",
            reply_markup=mileage_settings_keyboard(),
        )
    else:
        await message.answer(
            "Не удалось удалить настройку.",
            reply_markup=mileage_settings_keyboard(),
        )    




# =========================
# РУЧНОЙ ВВОД
# =========================

@router.message(lambda message: message.text == "Ручной ввод")
async def manual_input(message: Message):
    user = await get_user_by_telegram_id(message.from_user.id)

    if user is None or user.role not in ("operator", "administrator"):
        return

    await message.answer(
        "Ручной ввод:",
        reply_markup=manual_input_keyboard(),
    )




# =========================
# ПРОСМОТР
# =========================

@router.message(lambda message: message.text == "Просмотр")
async def viewer_section(message: Message):
    user = await get_user_by_telegram_id(message.from_user.id)

    if user is None or user.role != "administrator":
        return

    await message.answer(
        "Раздел просмотра:",
        reply_markup=viewer_keyboard(),
    )

@router.message(lambda message: message.text == "Настройка уведомлений")
async def notification_settings(message: Message):
    user = await get_user_by_telegram_id(message.from_user.id)

    if user is None or user.role not in ("viewer", "administrator"):
        return

    await message.answer(
        "Настройка уведомлений:",
        reply_markup=notification_settings_keyboard(),
    )





# =========================
# НАЗАД
# =========================

@router.message(lambda message: message.text == "Назад")
async def go_back(message: Message):
    user = await get_user_by_telegram_id(message.from_user.id)

    if user is None:
        return

    # Пока определяем возврат по текущему тексту/контексту
    # Дальше заменим это на полноценное управление состоянием меню.

    await show_main_menu(message, user)