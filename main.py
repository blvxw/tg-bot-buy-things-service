import asyncio
from packages.bot.bot import *
from packages.services.prisma_service import PrismaService

if __name__ == '__main__':    
    loop = asyncio.get_running_loop() if asyncio.get_event_loop().is_running() else asyncio.new_event_loop()
    loop.run_until_complete(PrismaService().connect())

    BotApp().start_polling()