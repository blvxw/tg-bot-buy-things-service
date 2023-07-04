from packages.bot.admin.handlers.admin_menu import admin_menu
from packages.bot.user.handlers.user_menu import user_menu

async def menu(isUser, bot, message, state,language):
    if isUser:
        await user_menu(bot, message, state,language)
    else:
        await admin_menu(bot, message, state,language)
    
    