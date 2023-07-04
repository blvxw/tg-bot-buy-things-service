from packages.utils.language import loadTextByLanguage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def menuKeyboard(lang):
    keyboard = InlineKeyboardMarkup()
    
    keyboard.row(
        InlineKeyboardButton('📃 Каталоги', callback_data='catalogs'),
        InlineKeyboardButton('🛒 Корзина', callback_data='cart'),
    )
    
    keyboard.row(
        InlineKeyboardButton('📦 Мої замовлення', callback_data='my_orders'),
        InlineKeyboardButton('⚙️ Налаштування', callback_data='settings'),
    )
    
    return keyboard
    