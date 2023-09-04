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
from packages.bot.admin.handlers.send_answer import *

# > MAIN ADMIN MENU <
@dp.callback_query_handler(lambda query: check_query(query, CallbackValues.SHOW_ADMIN_MAIN_MENU.value))
async def admin_menu(obj):
    if isinstance(obj, types.CallbackQuery):
        message = obj.message
    elif isinstance(obj, types.Message):
        message = obj

    language = await get_user_language(message.chat.id)
    await send_message(message.chat.id, load_text(language, 'admin_panel'), message.message_id, reply_markup=admin_menu_keyboard(language))

# > CHECK ORDERS <
@dp.callback_query_handler(lambda query: check_query(query, CallbackValues.SHOW_ADMIN_ORDERS_MENU.value))
async def call_orders_menu(query):
    await show_active_orders(query)


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

@dp.callback_query_handler(lambda query: check_query(query, 'answer_question'))
async def process_choose_question(query: types.CallbackQuery):
    question_id = query.data.split(':')[1]

    state = dp.current_state(user=query.from_user.id)
    await state.update_data(question_id=question_id)

    question = await PrismaService().get_question(question_id)
    keyboard = InlineKeyboardMarkup()
    lang = await get_user_language(query.from_user.id)
    keyboard.add(InlineKeyboardButton(text=load_text(lang,'back_btn'), callback_data=CallbackValues.SHOW_ADMIN_MAIN_MENU))
    await send_message(query.from_user.id,f"Питання: <i>{question.question}</i>\n\n<b>Введіть відповідь на запитання:</b>", query.message.message_id)
    await AdminMenuState.confirm_answer.set()


@dp.message_handler(state=AdminMenuState.confirm_answer)
async def confirm_answer(message,state):
    await state.reset_state(with_data=False)
    answer = message.text
    await state.update_data(answer=answer)

    data = await state.get_data()
    question_id = data.get('question_id')

    question = await PrismaService().get_question(question_id)

    text = f"Питання: <i>{question.question}</i>\n\nВідповідь: <i>{answer}</i>"

    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton("Надіслати", callback_data=f'{CallbackValues.ADMIN_SEND_ANSWER.value}:yes'),
    )
    keyboard.add(
        InlineKeyboardButton("Редагувати", callback_data=f'answer_question:{question_id}'),
    )
    keyboard.add(
        InlineKeyboardButton("Скасувати", callback_data=f'{CallbackValues.SHOW_ADMIN_MAIN_MENU.value}'),
    )

    await send_message(message.chat.id, text, message.message_id, reply_markup=keyboard)

@dp.callback_query_handler(lambda query: check_query(query, CallbackValues.ADMIN_SEND_ANSWER.value))
async def send_answer(query):
    state = dp.current_state(user=query.from_user.id)
    data = await state.get_data()
    question_id = data.get('question_id')
    answer = data.get('answer')

    question = await PrismaService().get_question(question_id)
    text = f"<b>Ви отримали відповідть на ваше запитання</b>\n\nПитання: <i>{question.question}</i>\n\nВідповідь: <i>{answer}</i>"
    user_id = question.user_telegram_id
    await bot.send_message(user_id, text)
    await query.answer("Відповідь надіслана користувачу ✅")
    await PrismaService().delete_question(question_id)
    await state.reset_state(with_data=False)
    await admin_menu(query)