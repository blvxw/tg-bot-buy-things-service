from services.prisma_service import PrismaService

class SingUp():
    def __init__(self):
        self.prisma_service = PrismaService()

    async def createUser(self,name,surname,phone,telegram_id,email,password,admin = False):      
        user = await self.prisma.user.create(
            data = {
                'name': name,
                'surname': surname,
                'phone': phone,
                'telegram_id': telegram_id,
                'email': email,
                'password': password,
                'role': 'ADMIN' if admin else 'USER'                      
            },
        )
        return user
