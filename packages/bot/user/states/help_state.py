from aiogram.dispatcher.filters.state import State, StatesGroup

class HelpState(StatesGroup):
    question = State()
