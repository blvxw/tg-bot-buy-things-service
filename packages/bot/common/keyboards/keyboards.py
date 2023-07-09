from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from packages.utils.language import loadTextByLanguage

def chooseLangKeyboard():
    keyboard = InlineKeyboardMarkup()
    
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

def yesOrNoKeyboard(lang):
    keyboard = InlineKeyboardMarkup()
    
    keyboard.row(
        InlineKeyboardButton(loadTextByLanguage(lang,'yes'), callback_data='yes'),
        InlineKeyboardButton(loadTextByLanguage(lang,'no'), callback_data='no'),
    )
    
    return keyboard

def generateCatalogsKeyboard(catalogs,callback_data):
    print(callback_data)
    keyboard = InlineKeyboardMarkup()
    row_btns = []
    
    for idx, catalog in enumerate(catalogs):
        row_btns.append(InlineKeyboardButton(catalog.name, callback_data=f"{callback_data}:{catalog.id}")) 
        
        if idx % 2 == 1 or idx == len(catalogs)-1:  
            keyboard.row(*row_btns)
            row_btns = []
            
    return keyboard

def cancelKeyboard(lang):
    keyboard = ReplyKeyboardMarkup()
    
    keyboard.row(
        KeyboardButton(loadTextByLanguage(lang,'cancel'), callback_data='cancel'),
    )
    
    return keyboard

def keyboard_for_product(index_product, total_products,index_media,total_media,callback_data):
    keyboard = InlineKeyboardMarkup(row_width=2)

    previous_product = InlineKeyboardButton("Назад", callback_data=f"{callback_data}:previous")
    next_product = InlineKeyboardButton("Вперед", callback_data=f"{callback_data}:next")
    num_of_product = InlineKeyboardButton(f"{index_product + 1}/{total_products}", callback_data=f"{callback_data}:num_of_product")
    
    previous_media = InlineKeyboardButton("Попереднє фото", callback_data=f"{callback_data}:previous_photo")
    next_media = InlineKeyboardButton("Наступне фото", callback_data=f"{callback_data}:next_photo")
    num_of_media = InlineKeyboardButton(f"{index_media + 1}/{total_media}", callback_data=f"{callback_data}:num_of_photo")
    
    keyboard.row(previous_media, num_of_media, next_media)
    keyboard.row(previous_product, num_of_product, next_product)
    
    add_to_cart_button = InlineKeyboardButton(
        "Додати до кошика",
        callback_data=f"add_to_cart:{index_product}"
    )
    
    keyboard.row(add_to_cart_button)

    return keyboard
