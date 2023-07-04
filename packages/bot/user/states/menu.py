from aiogram.dispatcher.filters.state import State, StatesGroup

class MenuState(StatesGroup):
    main = State()
    catalogs = State()
    products = State()
    cart = State()
    myOrders = State()
    settings = State()
