
# > keyboard
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# > data types
from packages.classes.user_callback import UserCallback

# > utils
from packages.utils.language import loadTextByLanguage


def mainMenuKeyboard(lang):
    keyboard = InlineKeyboardMarkup()

    keyboard.row(
        InlineKeyboardButton('📃 Каталоги',
                             callback_data=f'{UserCallback.USER_MAIN_MENU.value}:{UserCallback.USER_CATALOGS.value}'),
        InlineKeyboardButton('🛒 Корзина',
                             callback_data=f'{UserCallback.USER_MAIN_MENU.value}:{UserCallback.USER_CART.value}'),
    )

    keyboard.row(
        InlineKeyboardButton('📦 Мої замовлення',
                             callback_data=f'{UserCallback.USER_MAIN_MENU.value}:{UserCallback.USER_ORDERS.value}'),
        InlineKeyboardButton('⚙️ Налаштування',
                             callback_data=f'{UserCallback.USER_MAIN_MENU.value}:{UserCallback.USER_SETTINGS_MENU.value}'),
    )

    return keyboard


def settingsMenuKeyboard(user):
    keyboard = InlineKeyboardMarkup()

    if user.adultContent:
        btn_adult_content = InlineKeyboardButton('🔞 Відключити показ відвертого контенту',
                                                 callback_data=f'{UserCallback.CHOOSE_SHOW_ADULT_CONTENT.value}:no')
    else:
        btn_adult_content = InlineKeyboardButton('🔞 Включити показ відвертого контенту',
                                                 callback_data=f'{UserCallback.CHOOSE_SHOW_ADULT_CONTENT.value}:yes')

    keyboard.add(
        btn_adult_content,

        InlineKeyboardButton('🏴 Змінити мову',
                             callback_data=f'{UserCallback.USER_SETTINGS_MENU.value}:{UserCallback.CHANGE_LANGUAGE.value}')
    )

    return keyboard
