from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def adminMenuKeyboard(lang):
    markup = InlineKeyboardMarkup()
    
    markup.row(
        InlineKeyboardMarkup(text="📃 Додати категорію", callback_data="action:add_category"),
        InlineKeyboardButton(text="📦 Додати товар", callback_data="action:add_product"),
        InlineKeyboardMarkup(text="🔒 Заблоковано", callback_data="action:-"),
    )
    markup.row(
        InlineKeyboardMarkup(text="🔒 Заблоковано", callback_data="action:-"),
        InlineKeyboardMarkup(text="🔒 Заблоковано", callback_data="action:-"),
        InlineKeyboardMarkup(text="🔒 Заблоковано", callback_data="action:-"),
    )
    markup.row(
        InlineKeyboardMarkup(text="🔒 Заблоковано", callback_data="action:-"),
        InlineKeyboardMarkup(text="🔒 Заблоковано", callback_data="action:-")
    )
    
    return markup