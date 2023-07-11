#>> bot 
from packages.bot.bot_app import BotApp
from packages.bot.loader import bot

#>>> db
from packages.services.prisma_service import PrismaService

#>>> misc
from packages.utils.env import get_env_variable
import asyncio

async def start():
    await PrismaService().initialize()    
    try:
        BotApp().start_polling()
    except Exception as e:
        print(f'\033[91m[BOT]\033[0m {e}')
        await bot.send_message(get_env_variable("DEV_ID"), f'⚠️ <b>Bot stopped</b> ⚠️\n\n<b>ERROR</b>: {e}',parse_mode='HTML')
    finally:
        print(f'\033[91m[BOT]\033[0m Bot stopped')
        PrismaService().disconnect()

if __name__ == '__main__':
    asyncio.run(start())
  