from packages.bot.loader import dp, bot
from packages.services.prisma_service import PrismaService
from packages.utils.language import loadTextByLanguage
from packages.utils.check_query_data import isQueryDataValid
from packages.utils.user_utils import *

@dp.callback_query_handler(lambda query: isQueryDataValid(query, 'choose_show_adult_content'))
async def choose_show_adult_content(query):
    action = query.data.split(':')[1]
    
    user = await get_current_user(query.from_user.id)
    
    adultContent = True if action == 'yes' else False
    
    await PrismaService().setShowAdultContent(user.telegram_id, adultContent)

    user.adultContent = adultContent
    await update_current_user(query.from_user.id, user)
    
    await bot.send_message(query.message.chat.id, loadTextByLanguage(user.language, 'successfully_set'))