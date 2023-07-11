# >>> keyboards
from packages.bot.user.keyboards.keyboards import settingsMenuKeyboard

# >>> validation of query data
from packages.utils.check_query_data import isQueryDataValid

# >>> bot and dispatcher
from packages.bot.loader import dp, bot

# >>> utlis
from packages.utils.language import loadTextByLanguage
from packages.utils.user_utils import get_user_language

# >>> handlers
from packages.bot.common.handlers.choose_language import chooseLanguage
from packages.bot.common.handlers.show_adult_content import *

# >>> data types
from packages.classes.user_callback import UserCallback


async def settings_menu(query):
    user = await get_current_user(query.from_user.id)

    await bot.send_message(query.message.chat.id,
                           text=loadTextByLanguage(user.language, 'settings_menu'),
                           reply_markup=settingsMenuKeyboard(user))


@dp.callback_query_handler(lambda query: isQueryDataValid(query, UserCallback.USER_SETTINGS_MENU.value))
async def settings_menu_handler(query):
    action = query.data.split(':')[1]

    if action == UserCallback.CHANGE_LANGUAGE.value:
        user_language = await get_user_language(query.from_user.id)
        await chooseLanguage(query.message, auth=False, current_lang=user_language)
