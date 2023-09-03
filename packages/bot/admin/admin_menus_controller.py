# >>> data management
from packages.services.prisma_service import PrismaService

# >>> keyboards
from packages.bot.admin.keyboards.keyboards import admin_menu_keyboard

# >>> Bot
from aiogram import types
from packages.bot.loader import dp
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# >>> utils
from packages.utils.user_utils import *
from packages.utils.message_utils import send_message
from packages.utils.check_query_data import check_query
from packages.utils.language import load_text

# >>> structs
from packages.structs.callback_values import CallbackValues

# >>> hadnlers
from packages.bot.admin.handlers.orders import *

# > MAIN ADMIN MENU <
@dp.callback_query_handler(lambda query: check_query(query, CallbackValues.SHOW_ADMIN_MAIN_MENU.value))
async def admin_menu(obj):
    if isinstance(obj, types.CallbackQuery):
        message = obj.message
    elif isinstance(obj, types.Message):
        message = obj

    language = await get_user_language(message.chat.id)
    await send_message(message.chat.id, load_text(language, 'admin_panel'), message.message_id, reply_markup=admin_menu_keyboard(language))

# > CHECK QUESTION <
@dp.callback_query_handler(lambda query: check_query(query, CallbackValues.ADMIN_CHECK_QUESTIONS.value))
async def check_question(query: types.CallbackQuery):
    questions = await PrismaService().get_questions()

    lang = await get_user_language(query.from_user.id)
    if len(questions) == 0:
        await query.answer(load_text(lang,'no_questions'))
        return

    keyboard = InlineKeyboardMarkup()
    for question in questions:
        keyboard.add(InlineKeyboardButton(text=question.question, callback_data=f'answer_question:{question.id}'))

    await send_message(query.from_user.id,load_text(lang,'select_question') ,query.message.message_id,reply_markup=keyboard)

# > CHECK ORDERS <
@dp.callback_query_handler(lambda query: check_query(query, CallbackValues.SHOW_ADMIN_ORDERS_MENU.value))
async def call_orders_menu(query):
    await show_active_orders(query)
