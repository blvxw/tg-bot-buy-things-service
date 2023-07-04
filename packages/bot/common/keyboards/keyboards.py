from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from packages.utils.language import loadTextByLanguage

def chooseLangKeyboard():
    keyboard = InlineKeyboardMarkup()
    # ukrainian, russian, english,polish, use emoji for flags
    
    keyboard.row(
        InlineKeyboardButton('🇺🇦 Українська', callback_data='ua'),
        InlineKeyboardButton('🇷🇺 Русский', callback_data='ru'),
    )
    
    keyboard.row(
        InlineKeyboardButton('🇬🇧 English', callback_data='en'),
        InlineKeyboardButton('🇵🇱 Polski', callback_data='pl'),
    )
    
    return keyboard

def chooseRoleKeyboard(lang):
    keyboard = InlineKeyboardMarkup()
    
    keyboard.row(
        InlineKeyboardButton(loadTextByLanguage(lang,'admin'), callback_data='admin'),
        InlineKeyboardButton(loadTextByLanguage(lang,'user'), callback_data='user'),
    )
    
    return keyboard