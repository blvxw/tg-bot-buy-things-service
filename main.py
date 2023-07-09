import asyncio
from packages.bot.bot import *
from packages.services.prisma_service import PrismaService

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(PrismaService().connect())
    BotApp().start_polling()
