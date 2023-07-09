
# > patterns
from packages.patterns.singleton import Singleton
from aiogram import executor

from packages.bot.loader import *
from packages.bot.common.handlers.start import *

class BotApp(metaclass=Singleton):
    def __init__(self):
        self.bot = bot
        self.storage = storage
        self.dp = dp
        
    def start_polling(self):
        executor.start_polling(self.dp, skip_updates=True)

