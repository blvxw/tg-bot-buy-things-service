
# > bot and dispatcher ...
from packages.bot.loader import dp, bot
from aiogram.types import CallbackQuery

# > keyboards
from packages.bot.user.keyboards.keyboards import mainMenuKeyboard

# > validation of query data
from packages.utils.check_query_data import isQueryDataValid

# > user menus
from packages.bot.user.handlers.settings_menu import settings_menu
from packages.bot.user.handlers.main_menu.catalogs import catalogs

# > utils
from packages.utils.language import loadTextByLanguage
from packages.utils.user_utils import get_user_language

# > data types
from packages.classes.user_callback import UserCallback

async def user_menu(message):
    language = await get_user_language(message.from_user.id)
    await bot.send_message(message.chat.id, 'Панель керування', reply_markup=mainMenuKeyboard(language))

@dp.callback_query_handler(lambda query: isQueryDataValid(query, UserCallback.USER_MAIN_MENU.value))
async def menuHandler(query: CallbackQuery):
    action = query.data.split(':')[1]

    if action == UserCallback.USER_CATALOGS.value:
        await catalogs(query)
    elif action == UserCallback.USER_CART.value:
        # await show_cart(bot, query, state)
        pass
    elif action == UserCallback.USER_ORDERS.value:
        pass
    elif action == UserCallback.USER_SETTINGS_MENU.value:
        await settings_menu(query)


