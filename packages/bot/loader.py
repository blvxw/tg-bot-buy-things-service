from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from packages.utils.env import getEnvVar
from enum import Enum


class UserRoles(Enum):
    USER,
    ADMIN


bot = Bot(token=getEnvVar("BOT_TOKEN"), parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
