from packages.bot.common.states.get_info import GetInfo
from packages.bot.common.keyboards.keyboards import chooseLangKeyboard
from packages.utils.language import loadTextByLanguage
from packages.bot.common.handlers.auth.auth import auth
from packages.bot.loader import dp,bot
from packages.services.prisma_service import PrismaService

async def chooseLanguage(message,auth=False,current_lang=None):
    await bot.send_message(message.chat.id, "Choose language", reply_markup=chooseLangKeyboard(current_lang))
    state = dp.current_state(user=message.chat.id)
    await state.update_data(auth=auth)
    await GetInfo.chooseLanguageState.set()

@dp.callback_query_handler(lambda query: query.data in ['ua','ru','en','pl'], state=GetInfo.chooseLanguageState)
async def chooseLanguageHandler(query, state):
    await bot.answer_callback_query(query.id, text=loadTextByLanguage(query.data, 'language_selected'))
    await bot.delete_message(query.message.chat.id, query.message.message_id)
        
    data = await state.get_data()
    if data['auth'] == False:
        await PrismaService().updateUserLanguage(query.from_user.id, query.data)
        await state.finish()
        return
        
    await state.update_data(language=query.data)
    await auth(bot, query.message, state)
    
    