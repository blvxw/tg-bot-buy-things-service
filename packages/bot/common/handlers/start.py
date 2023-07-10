
# >>> Other handlers
from packages.bot.common.handlers.choose_language import chooseLanguage
from packages.bot.common.handlers.menu import menu

# >>> DB
from packages.services.prisma_service import PrismaService

# >>> Bot and Dispatcher ...
from packages.bot.loader import *
from aiogram.dispatcher import FSMContext

@dp.message_handler(commands=['start'])
async def start(message):
    print('\033[92m[BOT]\033[0m /start')
    user = await PrismaService().findUserByTelegramId(message.from_user.id)
    
    if user:
        await menu(user.role == UserRoles.USER.value, message, user.language)
    else:
        await chooseLanguage(bot, message)
