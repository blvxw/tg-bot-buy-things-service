# >>> BOT
from packages.bot.loader import dp, bot
from aiogram.types import CallbackQuery

# >>> DB
from packages.services.prisma_service import PrismaService

# >>> data types
from packages.structs.callback_values import CallbackValues

# >>> utils
from packages.utils.language import load_text
from packages.utils.message_utils import send_message
from packages.utils.user_utils import get_current_user
from packages.utils.check_query_data import check_query

# >>> keyboards
from packages.bot.common.keyboards import choose_language_keyboard
from packages.utils.user_utils import update_current_user

# >>> main menu
from packages.bot.user.user_menu_controller import show_user_menu

@dp.callback_query_handler(lambda query: check_query(query, CallbackValues.USER_CHANGE_LANGUAGE_MENU.value))
async def choose_language(message) -> None:
    if isinstance(message, CallbackQuery):
        message = message.message
    else:
        message = message
        
    user = await get_current_user(message.chat.id)
    if user is None:
        lang = None
    else:
        lang = user.language

    await send_message(message.chat.id, "Choose language", message.message_id, reply_markup=choose_language_keyboard(lang))

@dp.callback_query_handler(lambda query: check_query(query,'language'))
async def choose_language_handler(query) -> None:
    lang = query.data.split(':')[1]
    await bot.answer_callback_query(query.id, text=load_text(lang, 'language_selected'))
    
    user = await get_current_user(query.from_user.id)

    if user is None:
        await PrismaService().set_min_user_info(user_telegram_id=query.from_user.id, language=lang)
        await show_user_menu(query.message)
        return

    await PrismaService().set_user_language(query.from_user.id, lang)
    user.language = lang
    await update_current_user(query.from_user.id, user)
    await choose_language(query.message)
