from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    shift_action = State()
    photo = State()
    transfer = State()
    piecework = State()
