from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def adminMenuKeyboard(lang):
    markup = InlineKeyboardMarkup()
    
    markup.row(
        InlineKeyboardMarkup(text="📃 Додати категорію", callback_data="admin_menu:add_category"),
        InlineKeyboardButton(text="📦 Додати товар", callback_data="admin_menu:add_product"),
        InlineKeyboardMarkup(text="🔒 Заблоковано", callback_data="admin_menu:-"),
    )
    markup.row(
        InlineKeyboardMarkup(text="🔒 Заблоковано", callback_data="admin_menu:-"),
        InlineKeyboardMarkup(text="🔒 Заблоковано", callback_data="admin_menu:-"),
        InlineKeyboardMarkup(text="🔒 Заблоковано", callback_data="admin_menu:-"),
    )
    markup.row(
        InlineKeyboardMarkup(text="🔒 Заблоковано", callback_data="admin_menu:-"),
        InlineKeyboardMarkup(text="🔒 Заблоковано", callback_data="admin_menu:-")
    )
    
    return markup