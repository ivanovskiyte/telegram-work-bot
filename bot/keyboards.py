from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def admin_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Отчет за день"),
                KeyboardButton(text="Ручной ввод"),
            ],
            [
                KeyboardButton(text="Остаток в баке"),
                KeyboardButton(text="Изменить расход"),
            ],
            [
                KeyboardButton(text="Статистика"),
            ],
            [
                KeyboardButton(text="Дополнительно"),
            ],
        ],
        resize_keyboard=True,
    )


def operator_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Отчет за день"),
                KeyboardButton(text="Ручной ввод"),
            ],
            [
                KeyboardButton(text="Остаток в баке"),
                KeyboardButton(text="Изменить расход"),
            ],
            [
                KeyboardButton(text="Статистика"),
            ],
        ],
        resize_keyboard=True,
    )


def viewer_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Статистика по пользователю"),
                KeyboardButton(text="История отчетов"),
            ],
            [
                KeyboardButton(text="Отчет по пользователям за день"),
            ],
            [
                KeyboardButton(text="Настройка уведомлений"),
            ],
        ],
        resize_keyboard=True,
    )


def additional_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Администратор"),
                KeyboardButton(text="Просмотр"),
            ],
            [
                KeyboardButton(text="Назад"),
            ],
        ],
        resize_keyboard=True,
    )


def admin_section_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Управление пользователями"),
            ],
            [
                KeyboardButton(text="Назад"),
            ],
        ],
        resize_keyboard=True,
    )


def user_management_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Просмотр пользователей"),
            ],
            [
                KeyboardButton(text="Удаление пользователя"),
                KeyboardButton(text="Смена роли пользователя"),
            ],
            [
                KeyboardButton(text="Настройка километражей"),
                KeyboardButton(text="Настройка почты"),
            ],
            [
                KeyboardButton(text="Назад"),
            ],
        ],
        resize_keyboard=True,
    )


def manual_input_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Заправка"),
                KeyboardButton(text="Поездка"),
            ],
            [
                KeyboardButton(text="Выполненная работа"),
            ],
            [
                KeyboardButton(text="Назад"),
            ],
        ],
        resize_keyboard=True,
    )


def notification_settings_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Ежедневные уведомления в ТГ"),
            ],
            [
                KeyboardButton(text="Уведомления о заправке пользователя"),
            ],
            [
                KeyboardButton(text="Назад"),
            ],
        ],
        resize_keyboard=True,
    )



def mileage_settings_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Добавить"),
                KeyboardButton(text="Просмотреть"),
            ],
            [
                KeyboardButton(text="Удалить"),
            ],
            [
                KeyboardButton(text="Назад"),
            ],
        ],
        resize_keyboard=True,
    )