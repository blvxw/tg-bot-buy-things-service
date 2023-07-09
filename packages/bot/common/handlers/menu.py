from packages.bot.admin.handlers.admin_menu import admin_menu
from packages.bot.user.handlers.user_menu import user_menu

async def menu(isUser, message,language):
    if isUser:
        await user_menu(message,language)
    else:
        await admin_menu(message,language)
    
    