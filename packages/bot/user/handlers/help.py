# >>> bot and dispatcher
from packages.bot.loader import dp, bot

# >>> DB
from packages.services.prisma_service import PrismaService

# >>> states
from packages.bot.user.states.help_state import HelpState

# >>> keyboards
from packages.bot.common.keyboards import send_question_keyboard

# >>> data types
from packages.structs.callback_values import CallbackValues

# >>> utils
from packages.utils.user_utils import get_user_language
from packages.utils.message_utils import send_message
from packages.utils.language import load_text
from packages.utils.check_query_data import check_query

# >>> controller
from packages.bot.user.user_menu_controller import show_user_menu

@dp.message_handler(state=HelpState.question)
async def submit_question(message, state):
    await state.update_data(question=message.text)
    await state.reset_state(with_data=False)
    user_language = await get_user_language(message.chat.id)
    
    await send_message(message.chat.id, f"Запитання: <i>{message.text}</i> \n\n<b>Перевірте чи все правильно</b>", message.message_id, reply_markup=send_question_keyboard(user_language))

@dp.callback_query_handler(lambda query: check_query(query, CallbackValues.USER_MAIN_MENU.value), state=HelpState.question)
async def cancel_question(query, state):
    await state.reset_state(with_data=False)
    await show_user_menu(query.message)

@dp.callback_query_handler(lambda query: check_query(query, CallbackValues.SEND_QUESTION.value))
async def send_question_to_admins(query, state):
    action = query.data.split(':')[1]
    if action == 'yes':
        question = (await state.get_data())["question"]
        await bot.answer_callback_query(query.id, text="Ваше запитання відправлено адміністраторам")
        await show_user_menu(query.message)
        await PrismaService().send_question(query.from_user.id, question)