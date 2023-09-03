# >>> keyboard
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# >>> structs
from packages.structs.callback_values import CallbackValues

def admin_menu_keyboard(lang):
    keyboard = InlineKeyboardMarkup()
    
    keyboard.row(
        InlineKeyboardButton(text='📝 Редагувати вміст бази даних', callback_data=f'{CallbackValues.ADMIN_CATEGORIES.value}'),
    )

    keyboard.row(
        InlineKeyboardButton(text='📃 Замовлення', callback_data=f'{CallbackValues.SHOW_ADMIN_ORDERS_MENU.value}'),
        InlineKeyboardButton(text='❓ Питання', callback_data=f'{CallbackValues.ADMIN_CHECK_QUESTIONS.value}'),
    )

    keyboard.row(
        InlineKeyboardButton(text='👨‍💻 Користувацьке меню', callback_data=f'{CallbackValues.USER_MAIN_MENU.value}'),
    )

    return keyboard


def active_orders_keyboard(num_of_current_page,num_of_pages):
    keyboard = InlineKeyboardMarkup()

    keyboard.row(
        InlineKeyboardButton("⬅️", 
            callback_data=f"{CallbackValues.ADMIN_ORDERS_MENU_HANDLER.value}:{CallbackValues.PREVIOUS_ORDER.value}"),
        InlineKeyboardButton(f"{num_of_current_page + 1}/{num_of_pages}", 
            callback_data=f"{CallbackValues.ADMIN_ORDERS_MENU_HANDLER.value}:-"),
        InlineKeyboardButton("➡️",
            callback_data=f"{CallbackValues.ADMIN_ORDERS_MENU_HANDLER.value}:{CallbackValues.NEXT_ORDER.value}"),
    )

    keyboard.row(
        InlineKeyboardButton("📝 Змінити статус", 
                             callback_data=f"{CallbackValues.CHANGE_ORDER_STATUS.value}"),
        InlineKeyboardButton("📝 Коментар", callback_data=f"{CallbackValues.CHANGE_ORDER_COMMENT.value}"),
    )

    keyboard.row(
        InlineKeyboardButton("🔙 Назад", callback_data=f"{CallbackValues.SHOW_ADMIN_MAIN_MENU.value}"),
    )

    return keyboard

def order_status_keyboard(cur_order_status):
    in_progress = InlineKeyboardButton("В обробці", callback_data=f"{CallbackValues.SET_ORDER_STATUS.value}:{CallbackValues.IN_PROGRESS.value}")
    confirmed = InlineKeyboardButton("Прийнято", callback_data=f"{CallbackValues.SET_ORDER_STATUS.value}:{CallbackValues.CONFIRMED.value}")
    in_delivery = InlineKeyboardButton("В доставці", callback_data=f"{CallbackValues.SET_ORDER_STATUS.value}:{CallbackValues.IN_DELIVERY.value}")
    delivered = InlineKeyboardButton("Доставлено", callback_data=f"{CallbackValues.SET_ORDER_STATUS.value}:{CallbackValues.DELIVERED.value}")
    canceled = InlineKeyboardButton("Скасовано", callback_data=f"{CallbackValues.SET_ORDER_STATUS.value}:{CallbackValues.CANCELED.value}")

    status = {
        'in_progress': in_progress,
        'confirmed': confirmed,
        'in_delivery': in_delivery,
        'delivered': delivered,
        'canceled': canceled
    }

    status.pop(cur_order_status)
    keyboard = InlineKeyboardMarkup(row_width=1)

    keyboard.add(*status.values())
    keyboard.add(InlineKeyboardButton('🔙 Назад', callback_data=f'{CallbackValues.SHOW_ADMIN_ORDERS_MENU.value}'))

    return keyboard


def send_answer_keyboard(lang):
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton("Надіслати", callback_data=f'{CallbackValues.ADMIN_SEND_ANSWER.value}:yes'),
    )
    keyboard.add(
        InlineKeyboardButton("Редагувати", callback_data=f'{CallbackValues.ADMIN_.value}'),
    )
    keyboard.add(
        InlineKeyboardButton("Скасувати", callback_data=f'{CallbackValues.SHOW_ADMIN_MAIN_MENU.value}'),
    )
    
    return keyboard
