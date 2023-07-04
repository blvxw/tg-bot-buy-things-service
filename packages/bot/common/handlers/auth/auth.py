from packages.services.prisma_service import PrismaService
from packages.bot.common.handlers.auth.validation.auth_validation import AuthValidation
from packages.classes.user import User

from packages.utils.language import loadTextByLanguage
from packages.bot.common.states.get_info import GetInfo
from packages.bot.common.handlers.menu import menu

auth_validation = AuthValidation()

async def auth(bot, message, state):
    await bot.send_message(message.chat.id, "Давайте авторизуємося")

    data = await state.get_data()
    language = data['language']

    await bot.send_message(message.chat.id, loadTextByLanguage(language, 'enter_name'))
    await state.update_data(prompt='name')
    await GetInfo.authState.set()

async def getInfoHandler(bot, message, state):
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
        await create_user(bot,message,state,message.chat.id)
        await bot.send_message(message.chat.id, loadTextByLanguage(language, 'signup_success'))
    else:
        await bot.send_message(message.chat.id, "Invalid prompt")

async def handle_name(bot, message, state, language):
    name = message.text
    if not auth_validation.checkName(name):
        await bot.send_message(message.chat.id, loadTextByLanguage(language, 'signup_name_invalid'))
        return
    
    await bot.send_message(message.chat.id, loadTextByLanguage(language, 'enter_surname'))
    await state.update_data(name=name, prompt='surname')


async def handle_surname(bot, message, state, language):
    surname = message.text
    if not auth_validation.checkSurname(surname):
        await bot.send_message(message.chat.id, loadTextByLanguage(language, 'signup_surname_invalid'))
        return
    
    await bot.send_message(message.chat.id, loadTextByLanguage(language, 'enter_email'))
    await state.update_data(surname=surname, prompt='email')


async def handle_email(bot, message, state, language):
    email = message.text
    if not await auth_validation.checkEmail(email):
        await bot.send_message(message.chat.id, loadTextByLanguage(language, 'signup_email_invalid'))
        return

    await bot.send_message(message.chat.id, loadTextByLanguage(language, 'enter_phone'))
    await state.update_data(email=email, prompt='phone')


async def handle_phone(bot, message, state, language):
    phone = message.text
    if not await auth_validation.checkPhone(phone):
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
        language = data['language']
    )
    
    if user.allFieldsFilled() == False:
        return
    
    prisma_service = PrismaService()
    await prisma_service.addUser(user)
    
    await state.finish()
    await menu(user.role == 'USER', bot, message, state,user.language)