from packages.services.prisma_service import PrismaService
from packages.bot.common.handlers.choose_language import chooseLanguage
from packages.bot.common.handlers.auth.auth import auth
from packages.bot.common.handlers.menu import menu

async def start(bot, message, state):
    user = await PrismaService().findUserByTelegramId(message.from_user.id)
    if user == None:
        await chooseLanguage(bot, message, state)
    else:
        await menu(user.role == 'USER', bot, message, state,user.language)
