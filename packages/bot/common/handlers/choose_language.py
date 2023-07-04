from packages.bot.common.states.get_info import GetInfo
from packages.bot.common.keyboards.keyboards import chooseLangKeyboard
from packages.utils.language import loadTextByLanguage

from packages.bot.common.handlers.auth.auth import auth

async def chooseLanguage(bot, message, state):
    await bot.send_message(message.chat.id, "Choose language", reply_markup=chooseLangKeyboard())
    await GetInfo.chooseLanguageState.set()

async def chooseLanguageHandler(bot, query, state):
    await bot.answer_callback_query(query.id, text=loadTextByLanguage(query.data, 'language_selected'))
    await bot.delete_message(query.message.chat.id, query.message.message_id)
    await state.update_data(language=query.data)
  
    await auth(bot, query.message, state)

    
    