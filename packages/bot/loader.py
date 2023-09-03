from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from packages.utils.env import get_env_variable

#!
bot = Bot(token=get_env_variable("BOT_TOKEN_PROD"), parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
