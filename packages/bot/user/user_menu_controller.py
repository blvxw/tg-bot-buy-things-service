# >>> bot stuff
from packages.bot.loader import dp, bot
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton

# >>> DB
from packages.services.prisma_service import PrismaService

# >>> states
from packages.bot.user.states.help_state import HelpState

# >>> keyboards
from packages.bot.common.keyboards import back_btn,catalogs_keyboard
from packages.bot.user.keyboards.keyboards import main_menu_keyboard,settings_menu_keyboard

# >>> structs
from packages.structs.callback_values import CallbackValues
from packages.structs.user_roles import UserRoles

# >>> classes
from packages.bot.user.handlers.cart import Cart
from packages.bot.user.handlers.product_page import ProductPage

# >>> utils
from packages.utils.user_utils import get_user_language, get_current_user
from packages.utils.message_utils import send_message
from packages.utils.language import load_text
from packages.utils.check_query_data import check_query
from packages.utils.message_formaters import format_order_caption

# > MAIN MENU <
@dp.callback_query_handler(lambda query: check_query(query, CallbackValues.USER_MAIN_MENU.value))
async def show_user_menu(obj):
    if isinstance(obj, CallbackQuery):
        message = obj.message
    elif isinstance(obj, Message):
        message = obj
    
    user = await get_current_user(message.chat.id)
    reply_markup = main_menu_keyboard(user.language, user.role == UserRoles.ADMIN.value)
    await send_message(message.chat.id, "Панель керування", message.message_id, reply_markup)

# > SETTINGS MENU <
@dp.callback_query_handler(lambda query: check_query(query, CallbackValues.USER_SETTINGS_MENU.value))
async def show_settings_menu(query):
    user = await get_current_user(query.from_user.id)
    reply_markup = settings_menu_keyboard(user.language)
    number_of_messages = query.message.message_id
    await send_message(query.from_user.id, load_text(user.language, 'settings_menu'),
                       number_of_messages, reply_markup=reply_markup, parse_mode='HTML')

# > CATALOGS MENU <
@dp.callback_query_handler(lambda query: check_query(query, CallbackValues.USER_CATEGORIES_MENU.value))
async def show_categories(query):
    if isinstance(query, CallbackQuery):
        message = query.message
    elif isinstance(query, Message):
        message = query
   
    user = await get_current_user(message.chat.id)

    catalogs = await PrismaService().get_categories(user.adultContent)
    state = dp.current_state(user=message.from_user.id)
    await state.update_data(catalogs=catalogs)
    
    if len(catalogs) == 0:
        await send_message(message.chat.id, 'Немає категорій', message.message_id)
        return

    reply_markup = catalogs_keyboard(catalogs, CallbackValues.USER_SUBCATEGORIES_MENU.value)
    back_btn = InlineKeyboardButton(text="Назад", callback_data=CallbackValues.USER_MAIN_MENU.value)
    reply_markup.add(back_btn)

    await send_message(message.chat.id, "Оберіть каталог", message.message_id, reply_markup)

# >  SUBCATEGORIES MENU
@dp.callback_query_handler(lambda query: check_query(query, CallbackValues.USER_SUBCATEGORIES_MENU.value))
@dp.message_handler(text='📚 Назад до каталогів')
async def show_subcategories(obj):
    if isinstance(obj, CallbackQuery):
        message = obj.message
        category_id = obj.data.split(':')[1]
    elif isinstance(obj, Message):
        message = obj
        product_page = ProductPage.get_product_page(message)
        subcategory_id = product_page.subcategory_id
        # get id category from db by subcategory_id
        subcategory = await PrismaService().prisma.subcategory.find_first(where={'id': subcategory_id})
        category_id = subcategory.categoryId
        await product_page.delete_page()

    subcategories = await PrismaService().get_subcategories(category_id)

    if len(subcategories) == 0:
        await bot.send_message(message.chat.id, 'В цій категорії немає підкатегорій')
        return

    keyboard = catalogs_keyboard(subcategories, CallbackValues.USER_PRODUCTS_PAGE_MENU.value)
    back_btn = InlineKeyboardButton(text="Назад", callback_data=CallbackValues.USER_CATEGORIES_MENU.value)
    keyboard.add(back_btn)

    category = await PrismaService().get_category(category_id)
    await send_message(message.chat.id, f"{category.name}", message.message_id, keyboard)

# > PAGE OF PRODUCTS MENU
@dp.callback_query_handler(lambda query: check_query(query,CallbackValues.USER_PRODUCTS_PAGE_MENU.value))
async def show_page_of_products(query):
    product_page = ProductPage.get_product_page(query.message)
    subcategory_id = query.data.split(':')[1]
    await product_page.fetch_products(subcategory_id)

    if len(product_page.products) == 0:
        #*!
        await bot.answer_callback_query(query.id, 'В цій категорії немає товарів')
        return
    
    await bot.delete_message(query.message.chat.id, query.message.message_id)
    await product_page.show_page()

# >  CART MENU
@dp.callback_query_handler(lambda query: check_query(query, CallbackValues.USER_CART_MENU.value))
async def show_cart(query):
    cart = Cart.get_cart(query.message)
    await cart.fetch_cart_items()
    await cart.show_product(query)

# >  ORDER INFO
@dp.callback_query_handler(lambda query: check_query(query, CallbackValues.USER_ORDERS.value))
async def show_orders(query):
    user = await get_current_user(query.from_user.id)
    orders = await PrismaService().get_orders(user.id)

    if len(orders) == 0:
        await query.answer('У вас немає замовлень')
        return

    text = ''
    for order in orders:
        text += format_order_caption(order)
    
    reply_markup = back_btn(back_to=CallbackValues.USER_MAIN_MENU.value)
    await send_message(query.message.chat.id, text, query.message.message_id, reply_markup=reply_markup)

# >  QUESTION TO ADMINS
@dp.callback_query_handler(lambda query: check_query(query, CallbackValues.USER_HELP.value))
async def question_to_admins(query):
    flag = await PrismaService().user_alredy_send_question(query.from_user.id)

    if flag:
        await bot.answer_callback_query(query.id, text="Ви вже задали запитання, очікуйте відповіді")
        return

    await HelpState.question.set()
    reply_markup = back_btn(back_to=CallbackValues.USER_MAIN_MENU.value)
    await send_message(query.from_user.id, "<b>Напишіть запитання адміністраторам</b>", query.message.message_id, reply_markup=reply_markup)

# > ABOUT US
@dp.callback_query_handler(lambda query: check_query(query, CallbackValues.USER_ABOUT_US.value))
async def show_about_us(query):
    user = await get_current_user(query.from_user.id)
    reply_markup = back_btn(back_to=CallbackValues.USER_MAIN_MENU.value)
    await send_message(query.message.chat.id, "Про нас", query.message.message_id, reply_markup=reply_markup)