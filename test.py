import asyncio
from packages.services.prisma_service import PrismaService

async def main():
    await PrismaService().initialize()
    await PrismaService().clear_database()
    
if __name__ == '__main__':
    db_loop = asyncio.get_running_loop() if asyncio.get_event_loop().is_running() else asyncio.new_event_loop()
    db_loop.run_until_complete(main())
    