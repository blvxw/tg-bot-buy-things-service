
#> bot packages
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

#> handlers
from packages.bot.common.handlers.start import start
from packages.bot.common.handlers.choose_language import chooseLanguageHandler
from packages.bot.common.handlers.auth.auth import getInfoHandler

#> menu handlers
from packages.bot.admin.handlers.admin_menu import *
from packages.bot.user.handlers.user_menu import *

#> states
from packages.bot.common.states.get_info import GetInfo
from packages.bot.user.states.menu import MenuState
from packages.bot.admin.states.admin_state import AdminState

#> utils
from packages.utils.env import getEnvVar

#> dev
from packages.bot.spec.db_control import *

#> patterns
from packages.patterns.singleton import Singleton


class BotApp(metaclass=Singleton):
    def __init__(self):
        self.bot = Bot(token=getEnvVar('BOT_TOKEN'))
        self.dp = Dispatcher(self.bot, storage=MemoryStorage())
        
        self.dev_id = getEnvVar('DEV_ID')

        # > ######################################################################## <#
        # / __________________________ COMMON ________________________________________

        # ? __________________________ START ______________________________________
        @self.dp.message_handler(commands=['start','s','run','r','go'])
        async def _start(message: types.Message, state: FSMContext):
            print('\033[92m[BOT][COMMAND]\033[0m start')
            print(message.chat.id)
            await start(self.bot, message, state)

        # ? __________________________ CHOOSE LANGUAGE _____________________________

        @self.dp.callback_query_handler(state=GetInfo.chooseLanguageState)
        async def _chooseLanguageHandler(query: types.CallbackQuery, state: FSMContext):
            await chooseLanguageHandler(self.bot, query, state)

        # ? __________________________ AUTH _________________________________________
        @self.dp.message_handler(state=GetInfo.authState)
        async def _authHandler(message: types.Message, state: FSMContext):
            print('\033[92m[BOT][ACTION]\033[0m auth')
            await getInfoHandler(self.bot, message, state)

        # > ######################################################################## <#
        # / __________________________ USER _________________________________________

        # ? __________________________ MENU _________________________________________
        @self.dp.callback_query_handler(state=MenuState.main)
        async def _menuHandler(query: types.CallbackQuery, state: FSMContext):
            print('menu')
            await menuHandler(self.bot, query, state)

        # ? __________________________ CATALOGS _____________________________________
        @self.dp.callback_query_handler(state=MenuState.catalogs)
        async def _catalogsHandler(query: types.CallbackQuery, state: FSMContext):
            print('catalogs')
            await products_in_catalog(self.bot, query, state)

        # ? __________________________ PRODUCTS _____________________________________
        @self.dp.callback_query_handler(state=MenuState.products)
        async def _productsHandler(query: types.CallbackQuery, state: FSMContext):
            await handler_btn_product(self.bot, query, state)

        # > ######################################################################## <#
        # / __________________________ ADMIN ________________________________________

        # ? __________________________ ADMIN MENU ___________________________________
        @self.dp.callback_query_handler(state=AdminState.choose_action)
        async def _handle_choose_action(query: types.CallbackQuery, state: FSMContext):
            await handle_choose_action(self.bot, query, state)

        # ?#######################################################################################
        # ? __________________________ ADMIN ADD CATEGORY HANDLERS _____________________________
        @self.dp.message_handler(state=AdminState.create_category)
        async def _handle_create_category(message, state: FSMContext):
            await handle_create_category(self.bot,message, state)
        
        
        # ?#######################################################################################
        # ? __________________________ ADMIN ADD PRODUCT HANDLERS _______________________________
        @self.dp.callback_query_handler(state=AdminState.choose_category)
        async def _handle_choose_category(query: types.CallbackQuery, state: FSMContext):
            await handle_select_category(self.bot, query, state)

        @self.dp.message_handler(state=AdminState.add_name)
        async def _handle_add_name(message: types.Message, state: FSMContext):
            await handle_add_name(self.bot, message, state)

        @self.dp.message_handler(state=AdminState.add_description)
        async def _handle_add_item_description(message: types.Message, state: FSMContext):
            await handle_add_description(self.bot, message, state)

        @self.dp.message_handler(state=AdminState.add_price)
        async def _handle_add_price(message: types.Message, state: FSMContext):
            await handle_add_price(self.bot, message, state)

        @self.dp.message_handler(state=AdminState.add_discount)
        async def _handle_add_discount(message: types.Message, state: FSMContext):
            await handle_add_discount(self.bot, message, state)

        @self.dp.message_handler(state=AdminState.add_color)
        async def _handle_add_color(message: types.Message, state: FSMContext):
            await handle_add_color(self.bot, message, state)

        @self.dp.message_handler(state=AdminState.add_sizes)
        async def _handle_add_sizes(message: types.Message, state: FSMContext):
            await handle_add_sizes(self.bot, message, state)

        @self.dp.message_handler(state=AdminState.add_quantities)
        async def _handle_add_quantities(message: types.Message, state: FSMContext):
            await handle_add_quantities(self.bot, message, state)

        @self.dp.message_handler(state=AdminState.add_photos, content_types=[types.ContentType.PHOTO,types.ContentType.TEXT])
        async def _handle_add_photos(message: types.Message, state: FSMContext):
            if message.content_type == types.ContentType.PHOTO:
                await handle_add_photos(self.bot, message, state)
            if message.content_type == types.ContentType.TEXT:
                if message.text == '/done':
                    await handle_add_done(self.bot, message, state)

        @self.dp.message_handler(state=AdminState.add_variants)
        async def _handle_add_variants(message: types.Message, state: FSMContext):
            await handle_add_variants(self.bot, message, state)
        # ?#######################################################################################
        
        # > ######################################################################## <#
        # / __________________________ SPECIAL ________________________________________
        @self.dp.message_handler(commands=['clear_db'])
        async def _clear_db(message: types.Message, state: FSMContext):
            if message.chat.id in self.dev_id:
                await clear_database(self.bot, message, state)
                print('\033[92m[BOT][COMMAND]\033[0m clear_db')
                await self.bot.send_message(message.chat.id, 'Database cleared successfully 🗑️')
        
        @self.dp.message_handler(commands=['clear_users'])
        async def _clear_users(message: types.Message, state: FSMContext):
            if message.chat.id in self.dev_id:
                await clear_users(self.bot, message, state)
                print('\033[92m[BOT][COMMAND]\033[0m clear_users')
                await self.bot.send_message(message.chat.id, 'Users cleared successfully 🗑️')

        @self.dp.message_handler(commands=['clear_categories'])
        async def _clear_categories(message: types.Message, state: FSMContext):
            if message.chat.id in self.dev_id:
                await clear_categories(self.bot, message, state)
                print('\033[92m[BOT][COMMAND]\033[0m clear_categories')
                await self.bot.send_message(message.chat.id, 'Categories cleared successfully 🗑️')    
        
        @self.dp.message_handler(commands=['clear_products'])
        async def _clear_products(message: types.Message, state: FSMContext):
            if message.chat.id in self.dev_id:
                await clear_products(self.bot, message, state)
                print('\033[92m[BOT][COMMAND]\033[0m clear_products')
                await self.bot.send_message(message.chat.id, 'Products cleared successfully 🗑️')

        @self.dp.message_handler(commands=['clear_cart'])
        async def _clear_cart(message: types.Message, state: FSMContext):
            if message.chat.id in self.dev_id:
                await clear_cart_items(self.bot, message, state)
                print('\033[92m[BOT][COMMAND]\033[0m clear_cart')
                await self.bot.send_message(message.chat.id, 'Cart cleared successfully 🗑️')

    async def start_polling(self):
        print('\033[92m[BOT]\033[0m Bot started')
        await self.dp.start_polling()
