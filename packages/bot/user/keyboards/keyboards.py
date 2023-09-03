# >>> keyboard/btns types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# >>> structs
from packages.structs.callback_values import CallbackValues

# >>> utils
from packages.utils.language import load_text

def main_menu_keyboard(lang,is_admin=False):
    keyboard = InlineKeyboardMarkup(row_width=2,resize_keyboard=True)

    keyboard.row(
        InlineKeyboardButton('📃 Каталоги',
                             callback_data=f'{CallbackValues.USER_CATEGORIES_MENU.value}'),
        InlineKeyboardButton('🛒 Корзина',
                             callback_data=f'{CallbackValues.USER_CART_MENU.value}'),
        
    )
    
    keyboard.row(
        InlineKeyboardButton('📦 Мої замовлення',
                             callback_data=f'{CallbackValues.USER_ORDERS.value}'),
        
        InlineKeyboardButton('⚙️ Налаштування',
                             callback_data=f'{CallbackValues.USER_SETTINGS_MENU.value}'),
    )
    
    keyboard.row(
        InlineKeyboardButton('❓ Запитання',
                                callback_data=f'{CallbackValues.USER_HELP.value}'),
        InlineKeyboardButton('ℹ️ Про нас',
                                callback_data=f'{CallbackValues.USER_ABOUT_US.value}'),   
    )

    if is_admin:
        keyboard.row(
            InlineKeyboardButton('🔑 Панель адміністратора',
                                    callback_data=f'{CallbackValues.SHOW_ADMIN_MAIN_MENU.value}'),
        )

    return keyboard

def settings_menu_keyboard(lang):
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton('🔞 Налаштування відвертого контенту',
                                                 callback_data=f'{CallbackValues.USER_CHANGE_VALUE_ADULT_CONTENT.value}')
    )
    
    keyboard.add(
        InlineKeyboardButton('🏴 Змінити мову',
                             callback_data=f'{CallbackValues.USER_CHANGE_LANGUAGE_MENU.value}')
    )
  
    keyboard.add(
        InlineKeyboardButton('🔙 Назад',
                             callback_data=f'{CallbackValues.USER_MAIN_MENU.value}')
    )
    
    return keyboard

def cart_menu_keyboard(lang,cur_item, num_of_items, quantity,total_price):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    
    keyboard.row(
        InlineKeyboardButton("⬅️", callback_data=f"cart_product_btns:previous_product"),
        InlineKeyboardButton(f"{cur_item + 1}/{num_of_items}", callback_data=f"-"),
        InlineKeyboardButton("➡️", callback_data=f"cart_product_btns:next_product"),
    )
    keyboard.row(
        InlineKeyboardButton("➖", callback_data=f"cart_product_btns:minus_product"),
        InlineKeyboardButton(f"{quantity} шт.", callback_data=f"cart_product_btns:-"),
        InlineKeyboardButton("➕", callback_data=f"cart_product_btns:plus_product"),
    )
    keyboard.row(
        InlineKeyboardButton("Delete product ❌", callback_data=f"cart_product_btns:delete_product_from_cart"),
        InlineKeyboardButton("Delete cart ❌", callback_data=f"cart_product_btns:delete_all_products_from_cart"),
    )
    
    keyboard.row(
        InlineKeyboardButton(f"Total price 🪙: {total_price}", callback_data=f"cart_product_btns:-"),
        InlineKeyboardButton("Submit order 🚛", callback_data=f"cart_product_btns:submit_order"),
    )
    
    keyboard.add(
        InlineKeyboardButton('🔙 Назад',
                             callback_data=f'{CallbackValues.USER_MAIN_MENU.value}')
    )
    
    return keyboard

def edit_order_details_buttons(lang):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)

    keyboard.row(
        KeyboardButton(text="Відмінити"),
        KeyboardButton(text="Редагувати адресу")
    )

    return keyboard