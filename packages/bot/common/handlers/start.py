
# >>> Other handlers
from packages.bot.common.handlers.choose_language import chooseLanguage
from packages.bot.common.handlers.menu import menu

# >>> DB
from packages.services.prisma_service import PrismaService

# >>> Bot and Dispatcher
from packages.bot.loader import *

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    print("start")
    user = await PrismaService().findUserByTelegramId(message.from_user.id)
    state = dp.current_state(user=message.from_user.id)
    if user == None:
        await chooseLanguage(bot, message, state)
    else:
        await menu(user.role == UserRoles.USER.value, message, user.language)
