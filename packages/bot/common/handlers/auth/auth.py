from packages.services.prisma_service import PrismaService
from packages.bot.common.handlers.auth.validation.auth_validation import AuthValidation
from packages.classes.user import User

from packages.utils.language import loadTextByLanguage
from packages.bot.common.states.get_info import GetInfo
from packages.bot.loader import dp, bot

async def auth(bot, message, state):
    data = await state.get_data()
    language = data['language']

    await bot.send_message(message.chat.id, loadTextByLanguage(language, 'enter_name'))
    await state.update_data(prompt='name')
    await GetInfo.authState.set()

@dp.message_handler(state=GetInfo.authState)
async def getInfoHandler(message, state):
    data = await state.get_data()
    language = data['language']
    prompt = data['prompt']

    if prompt == 'name':
        await handle_name(bot, message, state, language)

    elif prompt == 'surname':
        await handle_surname(bot, message, state, language)

    elif prompt == 'email':
        await handle_email(bot, message, state, language)

    elif prompt == 'phone':
        await handle_phone(bot, message, state, language)
        data = await state.get_data()
        if data['prompt'] == 'password':
           return 
        await create_user(bot,message,state,message.chat.id)
        await bot.send_message(message.chat.id, loadTextByLanguage(language, 'signup_success'))
    else:
        await bot.send_message(message.chat.id, "Invalid prompt")

async def handle_name(bot, message, state, language):
    print(message.text)
    name = message.text
    if not AuthValidation().checkName(name):
        await bot.send_message(message.chat.id, loadTextByLanguage(language, 'signup_name_invalid'))
        return
    
    await bot.send_message(message.chat.id, loadTextByLanguage(language, 'enter_surname'))
    await state.update_data(name=name, prompt='surname')


async def handle_surname(bot, message, state, language):
    surname = message.text
    if not AuthValidation().checkSurname(surname):
        await bot.send_message(message.chat.id, loadTextByLanguage(language, 'signup_surname_invalid'))
        return
    
    await bot.send_message(message.chat.id, loadTextByLanguage(language, 'enter_email'))
    await state.update_data(surname=surname, prompt='email')


async def handle_email(bot, message, state, language):
    email = message.text
    if not await AuthValidation().checkEmail(email):
        await bot.send_message(message.chat.id, loadTextByLanguage(language, 'signup_email_invalid'))
        return

    await bot.send_message(message.chat.id, loadTextByLanguage(language, 'enter_phone'))
    await state.update_data(email=email, prompt='phone')


async def handle_phone(bot, message, state, language):
    phone = message.text
    if not await AuthValidation().checkPhone(phone):
        await bot.send_message(message.chat.id, loadTextByLanguage(language, 'signup_phone_invalid'))
        return

    await state.update_data(phone=phone)

async def create_user(bot,message,state,telegram_id):
    data = await state.get_data()
    user = User(
        telegram_id = telegram_id,
        name = data['name'],
        surname = data['surname'],
        phone = data['phone'],
        email = data['email'],
        language = data['language'],
        role = 'USER'
    )
    
    if user.allFieldsFilled() == False:
        return
    
    prisma_service = PrismaService()
    await prisma_service.addUser(user)
    await state.finish()