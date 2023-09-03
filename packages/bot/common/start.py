# >>> bot and dispatcher ...
from packages.bot.loader import dp

# >>> DB
from packages.services.prisma_service import PrismaService

# >>> utils
from packages.utils.user_utils import get_current_user,update_current_user

# >>> data types
from packages.structs.user_roles import UserRoles

# >>> handlers
from packages.bot.user.handlers.choose_language import choose_language

# >>> main menus
from packages.bot.admin.handlers.admin_menu import admin_menu
from packages.bot.user.user_menu_controller import show_user_menu

@dp.message_handler(commands=['start'])
async def start(message):
    print('\033[92m[BOT]\033[0m /start')
    user = await get_current_user(message.chat.id)

    if user == None:
        await choose_language(message)
        return

    if user.role is UserRoles.ADMIN: 
        await admin_menu(message)
    else:
        await show_user_menu(message)

@dp.message_handler(commands=['get_admin_rights'])
async def get_admin_rights(message):
    user = await get_current_user(message.chat.id)

    if user == None:
        await choose_language(message)
        return
    
    if user.role is UserRoles.ADMIN.value:
        await message.answer('Ви вже адміністратор')
        return
    
    user.role = UserRoles.ADMIN.value
    await PrismaService().change_user_role(user.telegram_id, UserRoles.ADMIN.value)
    await update_current_user(user.telegram_id,user)

    await message.answer('✅✅✅')

    await show_user_menu(message)

