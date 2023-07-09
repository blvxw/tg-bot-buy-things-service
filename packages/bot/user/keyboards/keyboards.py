from packages.utils.language import loadTextByLanguage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

user_menu_cb = CallbackData('catalogs', 'cart', 'orders', 'settings','action')

def menuKeyboard(lang):
    keyboard = InlineKeyboardMarkup()
    
    keyboard.row(
        InlineKeyboardButton('📃 Каталоги', callback_data='user_menu:catalogs'),
        InlineKeyboardButton('🛒 Корзина', callback_data='user_menu:cart'),
    )
    
    keyboard.row(
        InlineKeyboardButton('📦 Мої замовлення', callback_data='user_menu:orders'),
        InlineKeyboardButton('⚙️ Налаштування', callback_data='user_menu:action'),
    )
    
    return keyboard
    