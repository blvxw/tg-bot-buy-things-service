# >>> data management
from packages.services.prisma_service import PrismaService

# >>> states
from packages.bot.admin.states.admin_menu_state import AdminMenuState

# >>> Bot
from aiogram import types
from aiogram.dispatcher import FSMContext
from packages.bot.loader import dp, bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# >>> utils
from packages.utils.user_utils import *
from packages.utils.message_utils import send_message
from packages.utils.check_query_data import check_query
from packages.utils.language import load_text

# >>> structs
from packages.structs.callback_values import CallbackValues

# >>> controllers
from packages.bot.admin.admin_menus_controller import admin_menu

@dp.callback_query_handler(lambda query: check_query(query, 'answer_question'))
async def process_choose_question(query: types.CallbackQuery):
    question_id = query.data.split(':')[1]

    state = dp.current_state(user=query.from_user.id)
    await state.update_data(question_id=question_id)

    question = await PrismaService().get_question(question_id)
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="👈 Назад", callback_data="back"))
    await send_message(query.from_user.id,f"Питання: <i>{question.question}</i>\n\n<b>Введіть відповідь на запитання:</b>", query.message.message_id)
    await AdminMenuState.confirm_answer.set()

@dp.callback_query_handler(lambda query: check_query(query, 'Назад'), state=AdminMenuState.confirm_answer)
async def process_back(query: types.CallbackQuery, state: FSMContext):
    await state.reset_state(with_data=False)
    await admin_menu(query)

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
    await admin_menu(query)
