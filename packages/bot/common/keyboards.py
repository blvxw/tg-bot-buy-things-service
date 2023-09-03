from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from packages.utils.language import load_text
from packages.structs.callback_values import CallbackValues

def back_btn(back_to):
    keyboard = InlineKeyboardMarkup()

    keyboard.row(
        InlineKeyboardButton('🔙 Назад', callback_data=f'{back_to}')
    )

    return keyboard

def choose_language_keyboard(current_lang=None):
    keyboard = InlineKeyboardMarkup(row_width=2)

    ua = InlineKeyboardButton('🇺🇦 Українська', callback_data='language:ua')
    en = InlineKeyboardButton('🇬🇧 English', callback_data='language:en')
    ru = InlineKeyboardButton('🇷🇺 Русский', callback_data='language:ru')
    pl = InlineKeyboardButton('🇵🇱 Polski', callback_data='language:pl')

    languages = {
        'ua': ua,
        'en': en,
        'ru': ru,
        'pl': pl
    }

    if current_lang:
        languages.pop(current_lang)

    keyboard.add(*languages.values())

    if current_lang != None:
        keyboard.add(InlineKeyboardButton('🔙 Назад', callback_data=f'{CallbackValues.USER_SETTINGS_MENU.value}'))
        
    return keyboard

def send_question_keyboard(lang):
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton("Надіслати", callback_data=f'{CallbackValues.SEND_QUESTION.value}:yes'),
    )
    keyboard.add(
        InlineKeyboardButton("Редагувати", callback_data=f'{CallbackValues.USER_HELP.value}'),
    )
    keyboard.add(
        InlineKeyboardButton("Скасувати", callback_data=f'{CallbackValues.USER_MAIN_MENU.value}'),
    )
    
    return keyboard


def yes_no_keyboard(lang, callback_data = ""):
    keyboard = InlineKeyboardMarkup()

    keyboard.row(
        InlineKeyboardButton(load_text(lang, 'yes'), callback_data=f'{callback_data}:yes'),
        InlineKeyboardButton(load_text(lang, 'no'), callback_data=f'{callback_data}:no'),
    )

    return keyboard

def adult_content_keyboard(lang,show_adult_content):
    keyboard = InlineKeyboardMarkup()

    if show_adult_content:
        keyboard.row(
            InlineKeyboardButton("Увімкнути показ 🔞", callback_data=f'{CallbackValues.USER_CHANGE_VALUE_ADULT_CONTENT_HANDLER.value}:yes'),
        )
    else:
        keyboard.row(
            InlineKeyboardButton("Вимкнути показ 🔞", callback_data=f'{CallbackValues.USER_CHANGE_VALUE_ADULT_CONTENT_HANDLER.value}:no'),
        )

    return keyboard

def cancel_button(lang):
    keyboard = ReplyKeyboardMarkup()

    keyboard.row(
        KeyboardButton(load_text(lang, 'cancel'), callback_data='cancel'),
    )

    return keyboard

def product_keyboard(cur_media, num_of_media,callback_data,edit_mode=False):
    keyboard = InlineKeyboardMarkup()

    previous_media = InlineKeyboardButton("⬅️", callback_data=f"{callback_data}:previous_media")
    cur_media_btn = InlineKeyboardButton(f"{cur_media + 1}/{num_of_media}", callback_data=f"{callback_data}:-")
    next_media = InlineKeyboardButton("➡️", callback_data=f"{callback_data}:next_media")
    keyboard.row(previous_media, cur_media_btn, next_media)

    if edit_mode == False:
        keyboard.row(InlineKeyboardButton("🛒 Додати до кошика", callback_data=f"{callback_data}:add_to_cart"))
    else:
        keyboard.row(InlineKeyboardButton("🗑️ Видалити товар", callback_data=f"{callback_data}:delete_product"))

    return keyboard

def pages_keyboard(num_of_pages, num_of_current_page):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)

    keyboard.row(
        KeyboardButton("⬅️"),
        KeyboardButton(f"{num_of_current_page + 1}/{num_of_pages}"),
        KeyboardButton("➡️"),
    )
    keyboard.row(
        KeyboardButton('📚 Назад до каталогів')
    )

    return keyboard

def cansel_button(language):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)

    keyboard.row(
        KeyboardButton(text=load_text(language, 'cancel')),
    )

    return keyboard

def catalogs_keyboard(catalogs, callback_data):
    keyboard = InlineKeyboardMarkup()

    for catalog in catalogs:
        keyboard.row(
            InlineKeyboardButton(catalog.name, callback_data=f"{callback_data}:{catalog.id}")
        )

    return keyboard
