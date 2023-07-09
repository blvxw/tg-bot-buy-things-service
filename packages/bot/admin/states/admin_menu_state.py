from aiogram.dispatcher.filters.state import State, StatesGroup


class AdminMenuState(StatesGroup):
    choose_action = State()
    create_category = State()
    isAdultCategory = State()
    choose_category = State()
    add_name = State()
    add_description = State()
    add_price = State()
    add_discount = State()
    add_color = State()
    add_sizes = State()
    add_quantities = State()
    add_media = State()
    add_variants = State()
