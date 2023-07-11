import asyncio
from packages.bot.bot_app import BotApp
from packages.services.prisma_service import PrismaService

if __name__ == '__main__':
    db_loop = asyncio.get_running_loop() if asyncio.get_event_loop().is_running() else asyncio.new_event_loop()
    db_loop.run_until_complete(PrismaService().initialize())
    
    BotApp().start_polling()