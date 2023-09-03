# >>> bot
from aiogram import types
from packages.bot.loader import dp, bot
from aiogram.dispatcher import FSMContext

# >>> DB
from packages.services.prisma_service import PrismaService

# >>> validators
from packages.bot.user.handlers.auth.validation.auth_validation import AuthValidation

# >>> utils
from packages.utils.language import load_text
from packages.utils.user_utils import get_user_language
from packages.utils.message_utils import send_message
from packages.utils.user_utils import get_current_user

# >>> keyboards
from packages.bot.user.user_menu_controller import main_menu_keyboard

# >>> states
from packages.bot.user.states.get_info import GetInfo

# >>> structs
from packages.structs.user import User
from packages.structs.user_roles import UserRoles

class AuthHandler:
    def __init__(self, message: types.Message, state: FSMContext):
        self.message = message
        self.state = state
        self.language = None

        self.handlers = {
            'name': self.handle_name,
            'surname': self.handle_surname,
            'email': self.handle_email,
            'phone': self.handle_phone,
        }

    async def update_prompt(self, prompt):
        await self.state.update_data(prompt=prompt)

    async def set_language(self):
        if self.language is None:
            self.language = await get_user_language(self.message.chat.id)

    async def process_prompt(self):
        user_data = await self.state.get_data()
        prompt = user_data.get('prompt')

        if handler := self.handlers.get(prompt):
            await handler()

    async def handle_name(self):
        name = self.message.text
        if not AuthValidation().checkName(name):
            await self.message.reply(load_text(self.language, 'signup_name_invalid'))
            return
        await self.state.update_data(name=name)
        await self.message.reply(load_text(self.language, 'enter_surname'))
        await self.update_prompt('surname')

    async def handle_surname(self):
        surname = self.message.text
        if not AuthValidation().checkSurname(surname):
            await self.message.reply(load_text(self.language, 'signup_surname_invalid'))
            return
        await self.state.update_data(surname=surname)
        await self.message.reply(load_text(self.language, 'enter_email'))
        await self.update_prompt('email')

    async def handle_email(self):
        email = self.message.text
        if not await AuthValidation().checkEmail(email):
            await self.message.reply(load_text(self.language, 'signup_email_invalid'))
            return
        await self.state.update_data(email=email)
        await self.message.reply(load_text(self.language, 'enter_phone'))
        await self.update_prompt('phone')

    async def handle_phone(self):
        phone = self.message.text
        if not await AuthValidation().checkPhone(phone):
            await self.message.reply(load_text(self.language, 'signup_phone_invalid'))
            return
        await self.state.update_data(phone=phone)
        await self.create_user()

    async def create_user(self):
        data = await self.state.get_data()
        user = User(
            telegram_id=self.message.from_user.id,
            name=data['name'],
            surname=data['surname'],
            phone=data['phone'],
            email=data['email'],
            language=self.language,
        )
        if not user.allFieldsFilled():
            return

        prisma_service = PrismaService()
        await prisma_service.add_info_about_user(user)
        await self.state.reset_state(with_data=False)
        await bot.send_message(self.message.chat.id,'Інформація успішно збережена')

        user = await get_current_user(self.message.chat.id)
        reply_markup = main_menu_keyboard(user.language, user.role == UserRoles.ADMIN.value)
        await send_message(self.message.chat.id, "Панель керування", self.message.message_id, reply_markup)

@dp.message_handler(state=GetInfo.authState)
async def process_info(message: types.Message, state: FSMContext):
    auth_handler = AuthHandler(message, state)
    await auth_handler.set_language()
    await auth_handler.process_prompt()

async def process_auth(message: types.Message):
    language = await get_user_language(message.chat.id)
    await message.answer(load_text(language, 'enter_name'))

    state = dp.current_state(user=message.chat.id)
    await state.update_data(prompt='name')
    await GetInfo.authState.set()