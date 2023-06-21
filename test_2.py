from packages.services.prisma_service import PrismaService
import asyncio
import time

async def main():
    prisma_service = PrismaService()
    await prisma_service.initialize()
    print("prisma_service initialized")
    
    i = 1
    while True:
        time_start = time.time()
        # create new user
        await prisma_service.prisma.user.create(
            data={
                'name': 'test' + str(i),
                'surname': 'test' + str(i),
                'phone': 'test' + str(i),
                'telegram_id': 'test' + str(i),
                'email': 'test' + str(i),
                'password': 'test' + str(i),                
            }
            )
        print(f"{i}. user created - {time.time() - time_start} seconds")
        i += 1
        
if __name__ == '__main__':
    asyncio.run(main())