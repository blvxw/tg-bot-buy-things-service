import asyncio
from packages.bot.bot import BotApp
from packages.services.prisma_service import PrismaService

async def main():
    prisma_service = PrismaService()
    await prisma_service.initialize()
    bot = BotApp()
    await bot.start_polling()

if __name__ == '__main__':
    asyncio.run(main())
