from packages.bot.spec.db_control import clear_products
import asyncio
from packages.services.prisma_service import PrismaService

    
if __name__ == '__main__':
    asyncio.run(clear_products())