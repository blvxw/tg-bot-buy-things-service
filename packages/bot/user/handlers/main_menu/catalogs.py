
#> loader
from packages.bot.loader import bot

#> keyboards
from packages.bot.common.keyboards.keyboards import *

#> data types
from packages.classes.user_callback import UserCallback

#> utils
from packages.utils.user_utils import *

#> handler query
from packages.bot.user.handlers.main_menu.products import *

async def catalogs(query):
    adult_content: bool = (await get_current_user(query.from_user.id)).adultContent
    
    categories = await PrismaService().getAllCategories(adult_content)

    if len(categories) == 0:
        #* translate text
        await bot.send_message(query.message.chat.id, 'Каталогів немає')
        return

    await bot.send_message(query.message.chat.id, 'Каталоги', 
                           reply_markup=generateCatalogsKeyboard(categories, callback_data = UserCallback.USER_PRODUCTS_IN_CATALOG.value))
