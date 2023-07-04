from packages.bot.components.menu.form import Form
from packages.bot.components.menu.keyboards import chooseRoleKeyboard
from packages.utils.language import loadTextByLanguage
from packages.services.prisma_service import PrismaService
from packages.bot.admin.handlers.admin_menu import adminMenu


async def chooseRole(bot, message, state):
    print('chooseRole')
    prisma_service = PrismaService()
    user = await prisma_service.findUserByTelegramId(message.from_user.id)

    # create language in state
    await state.update_data(language=user.language)

    await bot.send_message(message.from_user.id, loadTextByLanguage(user.language, "choose_role"), reply_markup=chooseRoleKeyboard(user.language))
    await Form.choose_role.set()


async def chooseRoleHandler(bot, query, state):
    role = query.data
    data = await state.get_data()

    text = loadTextByLanguage(data['language'], query.data) + '✅'
    await bot.answer_callback_query(query.id, text=text)
    await bot.delete_message(query.message.chat.id, query.message.message_id)
    await state.update_data(role=role)

    if role == 'admin':
        await adminMenu(bot, query, state)
