# > bot stuff
from aiogram import executor
from packages.bot.loader import *

# > handlers
from packages.bot.common.handlers.start import *

class BotApp():
    def __init__(self):
        self.bot = bot
        self.storage = storage
        self.dp = dp

    def start_polling(self):
        print('\033[92m[BOT]\033[0m Bot started')
        executor.start_polling(self.dp, skip_updates=True)
    def stop_polling(self):
        print('\033[92m[BOT]\033[0m Bot stopped')
        executor.stop_polling(self.dp)