from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    choosing_role = State()
    entering_fuel_consumption = State()