from services.prisma_service import PrismaService
from globals.constants import USER_NOT_FOUND, PASSWORD_INCORRECT

class Login:
    def __init__(self):
        self.prisma_service = PrismaService()

    async def auth(self, email, password):
        user = await self.prisma_service.prisma.user.find_unique(
            where={'email': email}
        )
        
        await self.prisma_service.prisma.user.update(data={'logined': True},)
        
        if user is None:
            return USER_NOT_FOUND
        
        if user.password != password:
            return PASSWORD_INCORRECT
        
        return user    
        