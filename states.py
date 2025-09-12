from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    shift_action = State()
    photo = State()
    transfer_current = State()
    transfer_current_location = State()  # новое состояние для выбора текущего объекта
    transfer_new = State()
    transfer_new_location = State()      # новое состояние для выбора нового объекта
    transfer_names = State()
    piecework = State()