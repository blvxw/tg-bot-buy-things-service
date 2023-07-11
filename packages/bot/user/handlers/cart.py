from packages.services.prisma_service import PrismaService
from aiogram.types import ChatActions
from loader import bot

async def show_cart(query):
    await bot.send_chat_action(query.message.chat.id, ChatActions.TYPING)

    cart = await PrismaService().get_cart(query.message.chat.id)

    if cart == []:
        await bot.send_message(query.message.chat.id, "Кошик пустий")
        return
    