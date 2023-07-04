import json
from packages.services.prisma_service import PrismaService

async def getTextByTelegramId(telegram_id,text):
    language = await PrismaService().getLangByTelegramId(telegram_id)
    return loadTextByLanguage(language,text)
    
def loadTextByLanguage(language,text):
    with open('resources/languages/languages.json', encoding='utf-8') as f:
        data = json.load(f)
        return data[language][text]

