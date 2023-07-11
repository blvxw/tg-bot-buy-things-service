from packages.bot.admin.handlers.admin_menu import admin_menu
from packages.bot.user.handlers.main_menu.user_main_menu import user_menu

async def menu(isUser, message):
    await user_menu(message) if isUser else await admin_menu(message)