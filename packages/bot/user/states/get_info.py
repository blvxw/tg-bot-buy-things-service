from aiogram.dispatcher.filters.state import State, StatesGroup

class GetInfo(StatesGroup):
    chooseLanguageState = State()
    authState = State()