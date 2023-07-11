
# >>> Other handlers
from packages.bot.common.handlers.choose_language import chooseLanguage
from packages.bot.common.handlers.menu import menu

# >>> Bot and Dispatcher ...
from packages.bot.loader import *

# >>> Utils
from packages.utils.user_utils import *

# >>> data types
from packages.classes.user_roles import UserRoles

@dp.message_handler(commands=['start'])
async def start(message):
    print('\033[92m[BOT]\033[0m /start')
    user = await get_current_user(message.from_user.id)
    
    if user == None:
        await chooseLanguage(message, auth=True)
        return

    await menu(user.role == UserRoles.USER.value, message)
    