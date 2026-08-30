from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    choosing_role = State()
    entering_fuel_consumption = State()

class AdminStates(StatesGroup):
    deleting_user = State()
    confirming_deletion = State()

    changing_role = State()
    selecting_new_role = State()
    entering_new_fuel_consumption = State()
    confirming_role_change = State()
    adding_mileage_workplace = State()
    adding_mileage_value = State()
    deleting_mileage = State()
    confirming_mileage_deletion = State()

class DailyReportStates(StatesGroup):
    entering_workplace = State()
    confirming_mileage = State()
    entering_mileage = State()
    answering_refueling = State()
    entering_fuel_liters = State()
    entering_fuel_amount = State()
    entering_work_description = State()
    answering_work_completed = State()