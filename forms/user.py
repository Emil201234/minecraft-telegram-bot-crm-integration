from aiogram.fsm.state import StatesGroup, State

class Form_user(StatesGroup):
    nickname = State()
    password = State()