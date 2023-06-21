import prisma
from packages.patterns.singleton import Singleton
import asyncio
#! add singleton pattern
class PrismaService():
    def __init__(self):
        self.prisma = prisma.Prisma()

    async def initialize(self):
        await self.connect()

    async def connect(self):
        await self.prisma.connect()

    async def disconnect(self):
        await self.prisma.disconnect()

