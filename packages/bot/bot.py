from aiogram import Bot, Dispatcher, types
from packages.bot.methods.start import start
from packages.utils.env import getEnvVar
import asyncio
import time

class BotApp:
    def __init__(self):
        self.bot = Bot(token=getEnvVar('BOT_TOKEN'))
        self.dp = Dispatcher(self.bot)

        @self.dp.message_handler(commands=['start'])
        async def _start(message: types.Message):
            # check time
            time_start = time.time()
            # send my tg id
            # await message.answer(message.chat.id)
            await start(self, message)
            
            time_end = time.time()
            print('time: ', time_end - time_start)

    def run(self):
        asyncio.run(self.start_polling())

    async def start_polling(self):
        await self.dp.start_polling()

if __name__ == '__main__':
    bot = BotApp()
    bot.run()
