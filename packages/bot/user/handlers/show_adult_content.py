# >>> bot
from packages.bot.loader import dp, bot
from aiogram.types import InlineKeyboardButton

# >>> db
from packages.services.prisma_service import PrismaService

# >>> keyboard
from packages.bot.common.keyboards import adult_content_keyboard

# >>> structs
from packages.structs.callback_values import CallbackValues

# >>> utils
from packages.utils.check_query_data import check_query
from packages.utils.language import load_text
from packages.utils.user_utils import get_current_user,update_current_user
from packages.utils.message_utils import send_message

@dp.callback_query_handler(lambda query: check_query(query, CallbackValues.USER_CHANGE_VALUE_ADULT_CONTENT.value))
async def choose_show_adult_content(query):
    user = await get_current_user(query.from_user.id)

    keyboard = adult_content_keyboard(user.language, user.adultContent is False)
    
    keyboard.add(
        InlineKeyboardButton("🔙 Назад", callback_data=CallbackValues.USER_SETTINGS_MENU.value)
    )

    await send_message(query.from_user.id, "Відображати контент для дорослих?", query.message.message_id, reply_markup=keyboard)    

@dp.callback_query_handler(lambda query: check_query(query, CallbackValues.USER_CHANGE_VALUE_ADULT_CONTENT_HANDLER.value))
async def handle_user_choise(query):
    user = await get_current_user(query.from_user.id)
    user_choise = query.data.split(':')[1]
    
    if user_choise == 'yes':
        user.adultContent = True
        await bot.answer_callback_query(query.id, "Показ відкритого контенту увімкнено")
    elif user_choise == 'no':
        user.adultContent = False
        await bot.answer_callback_query(query.id, "Показ відкритого контенту вимкнено")

    print(query.from_user.id)
    await update_current_user(query.from_user.id, user)
    await choose_show_adult_content(query) #* UPDATE MESSAGE
    await PrismaService().show_for_user_adult_content(user.id, user.adultContent)