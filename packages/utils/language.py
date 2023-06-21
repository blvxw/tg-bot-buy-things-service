import json
from packages.services.prisma_service import PrismaService

async def getText(telegram_id,text):
    language = await getLang(telegram_id)
    # load data from json file only message which user need
    with open('resources/languages/languages.json', encoding='utf-8') as f:
        data = json.load(f)
        return data[language][text]
    

async def getLang(telegram_id):
    prismaService = PrismaService()
    user = await prismaService.prisma.user.find_first(where={"telegram_id": str(telegram_id)})
    return user.language
