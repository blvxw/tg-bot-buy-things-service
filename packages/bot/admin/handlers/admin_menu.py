# >>> system imports
import os

# >>> data management
from packages.services.prisma_service import PrismaService
from packages.services.firebase_storage import FirebaseStorage

# >>> structs
from packages.structs.product import Product
from packages.structs.product_variant import ProductVariant
from packages.structs.size import Size
from packages.structs.discount import Discount

# >>> keyboards
from packages.bot.admin.keyboards.keyboards import admin_menu_keyboard,send_answer_keyboard
from packages.bot.common.keyboards import catalogs_keyboard, yes_no_keyboard

# >>> states
from packages.bot.admin.states.admin_menu_state import AdminMenuState

# >>> Bot
from aiogram import types
from aiogram.dispatcher import FSMContext
from packages.bot.loader import dp, bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# >>> path
from resources.media.get_path import get_path_to_media_folder

# >>> utils
from packages.utils.user_utils import *
from packages.utils.message_utils import send_message
from packages.utils.check_query_data import check_query
from packages.utils.language import load_text

from packages.structs.callback_values import CallbackValues
from packages.bot.user.handlers.product_page import ProductPage

from packages.bot.admin.admin_menus_controller import admin_menu

language = None

@dp.callback_query_handler(lambda query: check_query(query, CallbackValues.ADMIN_CATEGORIES.value), state='*')
async def category_menu(query: types.CallbackQuery):
    state = dp.current_state(user=query.from_user.id)
    if isinstance(query, types.CallbackQuery):
        message = query.message
    elif isinstance(query, types.Message):
        message = query

    global language
    language = await get_user_language(message.chat.id)

    categories = await PrismaService().get_categories(adultContent=True)

    keyboard = catalogs_keyboard(categories, CallbackValues.ADMIN_CATEGORY_MENU.value)
    add_category_btn = InlineKeyboardButton(text=load_text(language,"add_category_btn"), callback_data='add_category')
    back_btn = InlineKeyboardButton(text=load_text(language,'back_btn'), callback_data=CallbackValues.SHOW_ADMIN_MAIN_MENU.value)
    keyboard.add(add_category_btn)
    keyboard.add(back_btn)

    await send_message(query.from_user.id, load_text(language,'categories'), message.message_id, reply_markup=keyboard)

@dp.callback_query_handler(lambda query: check_query(query, CallbackValues.ADMIN_CATEGORY_MENU.value), state='*')
async def process_catalogs_menu(obj: types.CallbackQuery):

    if isinstance(obj, types.CallbackQuery):
        message = obj.message
        category_id = obj.data.split(':')[1]
    elif isinstance(obj, types.Message):
        message = obj
        state = dp.current_state(user=message.chat.id)
        data = await state.get_data()
        category_id = data.get('category_id')
    state = dp.current_state(user=message.chat.id)
    await state.reset_state(with_data=False)

    subcategories = await PrismaService().get_subcategories(category_id)
    category = await PrismaService().get_category(category_id)

    add_subcategory_btn = InlineKeyboardButton(text=load_text(language,"add_subcategory_btn"), callback_data=f'add_subcategory:{category_id}')
    # delete_cur_catalog_btn = InlineKeyboardButton(text=load_text(language,"delete_cur_catalog_btn"), callback_data=f'delete_catalog:{category_id}')
    back_btn = InlineKeyboardButton(text=load_text(language,'back_btn'), callback_data=CallbackValues.ADMIN_CATEGORIES.value)

    keyboard = catalogs_keyboard(subcategories, CallbackValues.ADMIN_SUBCATEGORY_MENU.value)
    keyboard.add(add_subcategory_btn)
    # keyboard.add(delete_cur_catalog_btn)
    keyboard.add(back_btn)

    await send_message(message.chat.id, f"📖 <b>{category.name}</b>", message.message_id, reply_markup=keyboard)

@dp.callback_query_handler(lambda query: check_query(query, CallbackValues.ADMIN_SUBCATEGORY_MENU.value), state='*')
async def process_subcategories_menu(query: types.CallbackQuery):
    state = dp.current_state(user=query.from_user.id)
    await state.reset_state(with_data=False)
    
    subcategory_id = query.data.split(':')[1]
    subcategory = await PrismaService().get_subcategory(subcategory_id)
    keyboard = InlineKeyboardMarkup()

    # show_products_btn = InlineKeyboardButton(text=load_text(language,'show_products_btn'), callback_data=f'show_products:{subcategory_id}')
    add_product_btn = InlineKeyboardButton(text=load_text(language,'add_product_btn'), callback_data=f'add_product:{subcategory_id}')
    # delete_cur_subcategory_btn = InlineKeyboardButton(text=load_text(language,"delete_cur_subcategory_btn"), callback_data=f'delete_subcategory:{subcategory_id}')
    back_btn = InlineKeyboardButton(text="👈 Назад", callback_data=f'{CallbackValues.ADMIN_CATEGORY_MENU.value}:{subcategory.categoryId}')

    # keyboard.add(show_products_btn)
    keyboard.add(add_product_btn)
    # keyboard.add(delete_cur_subcaqtegory_btn)
    keyboard.add(back_btn)

    await send_message(query.from_user.id, f"📄 <b>{subcategory.name}</b>", query.message.message_id, reply_markup=keyboard)

# @dp.callback_query_handler(lambda query: check_query(query, 'show_products'))
# async def show_products_menu(query: types.CallbackQuery):
#     product_page = ProductPage.get_product_page(query.message, edit_mode=True)
#     subcategory_id = query.data.split(':')[1]
#     await product_page.fetch_products(subcategory_id)
    
#     if len(product_page.products) == 0:
#         #*!
#         await bot.answer_callback_query(query.id, 'В цій категорії немає товарів')
#         return
    
#     await bot.delete_message(query.message.chat.id, query.message.message_id)
    # await product_page.show_page()
    

@dp.callback_query_handler(lambda query: check_query(query, 'add_category'))
async def add_category(query: types.CallbackQuery):
    message = query.message
    keyboard = InlineKeyboardMarkup()
    back_btn = InlineKeyboardButton(text=load_text(language,'back_btn'), callback_data=CallbackValues.ADMIN_CATEGORIES.value)
    keyboard.add(back_btn)
    await send_message(message.chat.id,load_text(language,'enter_category_name') , message.message_id, reply_markup=keyboard)
    await AdminMenuState.isAdultCategory.set()

@dp.message_handler(state=AdminMenuState.isAdultCategory)
async def process_isAdultCategory(message: types.Message, state: FSMContext):
    category_name = message.text
    await state.update_data(category_name=category_name)
    keyboard = yes_no_keyboard(language,'is_adult_category_chooice')
    await send_message(message.chat.id, load_text(language,'is_adult_category'), message.message_id, reply_markup=keyboard)
    await state.reset_state(with_data=False)

@dp.callback_query_handler(lambda query: check_query(query, 'is_adult_category_chooice'))
async def process_create_category(query: types.Message, state: FSMContext):
    chooice = query.data.split(':')[1]
    data = await state.get_data()
    category_name = data.get('category_name')
    flag = await PrismaService().create_category(category_name, chooice == 'yes')

    if flag == False:
        await bot.send_message(query.from_user.id, load_text(language,'category_alredy_exists'))
        await admin_menu(query.message)
        return
    await category_menu(query)
    await bot.send_message(query.from_user.id, load_text(language,'category_added'))


@dp.callback_query_handler(lambda query: check_query(query, 'add_subcategory'))
async def add_subcategory(query: types.CallbackQuery):
    category_id = query.data.split(':')[1]
    state = dp.current_state(user=query.from_user.id)
    await state.update_data(category_id=category_id)
    message = query.message
    keyboard = InlineKeyboardMarkup()
    back_btn = InlineKeyboardButton(text=load_text(language,'back_btn'), callback_data=f'{CallbackValues.ADMIN_CATEGORY_MENU.value}:{category_id}')
    keyboard.add(back_btn)
    await send_message(message.chat.id, load_text(language,'enter_subcategory_name'), message.message_id, reply_markup=keyboard)
    await AdminMenuState.create_subcategory.set()

@dp.message_handler(state=AdminMenuState.create_subcategory)
async def process_create_subcategory(message: types.Message, state: FSMContext):
    await state.reset_state(with_data=False)
    subcategory_name = message.text
    data = await state.get_data()
    category_id = data.get('category_id')
    flag = await PrismaService().create_subcategory(subcategory_name, category_id)
    if flag == False:
        await bot.send_message(message.chat.id, load_text(language,'subcategory_alredy_exists'))
        await admin_menu(message)
        return
    
    await bot.send_message(message.chat.id, load_text(language,'subcategory_added'))
    await process_catalogs_menu(message)

@dp.callback_query_handler(lambda query: check_query(query, 'add_product'))
async def get_name_product(query, state: FSMContext):
    await state.update_data(subcategory_id=query.data.split(':')[1])
    await bot.send_message(query.from_user.id, load_text(language,'add_name'))
    await AdminMenuState.add_name.set()

@dp.message_handler(state=AdminMenuState.add_name)
async def process_add_name(message: types.Message, state: FSMContext):
    item_name = message.text
    await state.update_data(item_name=item_name)
    await bot.send_message(message.chat.id, load_text(language, 'add_description'))
    await AdminMenuState.add_description.set()


@dp.message_handler(state=AdminMenuState.add_description)
async def process_add_description(message: types.Message, state: FSMContext):
    item_description = message.text
    await state.update_data(item_description=item_description)
    await bot.send_message(message.chat.id, load_text(language, 'add_price'))
    await AdminMenuState.add_price.set()


@dp.message_handler(state=AdminMenuState.add_price)
async def process_add_price(message: types.Message, state: FSMContext):
    try:
        item_price = float(message.text)
        await state.update_data(item_price=item_price)
        await bot.send_message(message.chat.id, load_text(language, 'add_discount'))
        await AdminMenuState.add_discount.set()
    except ValueError:
        await bot.send_message(message.chat.id, load_text(language, 'incorrect_price'))


@dp.message_handler(state=AdminMenuState.add_discount)
async def process_add_discount(message: types.Message, state: FSMContext):
    try:
        item_discount = float(message.text)
        await state.update_data(item_discount=item_discount)
        await bot.send_message(message.chat.id, 'Закупочна ціна товару')
        await AdminMenuState.add_purchasing_price.set()
    except ValueError:
        await bot.send_message(message.chat.id, load_text(language, 'incorrect_discount'))

@dp.message_handler(state=AdminMenuState.add_purchasing_price)
async def process_add_purchasing_price(message: types.Message, state: FSMContext):
    try:
        item_purchasing_price = float(message.text)
        await state.update_data(item_purchasing_price=item_purchasing_price)
        await bot.send_message(message.chat.id, load_text(language, 'enter_color_product'))
        await AdminMenuState.add_color.set()
    except ValueError:
        await bot.send_message(message.chat.id, load_text(language, 'incorrect_price'))


@dp.message_handler(state=AdminMenuState.add_color)
async def process_add_color(message: types.Message, state: FSMContext):
    item_color = message.text.lower()
    await state.update_data(item_color=item_color)

    await bot.send_message(message.chat.id, load_text(language, 'enter_sizes_product'))
    await AdminMenuState.add_sizes.set()


@dp.message_handler(state=AdminMenuState.add_sizes)
async def process_add_sizes(message: types.Message, state: FSMContext):
    item_sizes = message.text.split(',')
    item_sizes = [size.strip().lower() for size in item_sizes]  # Переводимо розміри до маленьких літер
    await state.update_data(item_sizes=item_sizes)

    await bot.send_message(message.chat.id, load_text(language, 'enter_quantities_product'))
    await AdminMenuState.add_quantities.set()


@dp.message_handler(state=AdminMenuState.add_quantities)
async def process_add_quantities(message: types.Message, state: FSMContext):
    item_quantities = message.text.split(',')
    try:
        item_quantities = [int(quantity.strip()) for quantity in item_quantities]

        data = await state.get_data()
        item_sizes = data.get('item_sizes')

        if len(item_sizes) != len(item_quantities):
            await bot.send_message(message.chat.id, load_text(language, 'error_quntity_sizes'))
            return

    except ValueError:
        await bot.send_message(message.chat.id, load_text(language, 'incorrect_value_must_be_int'))
        return

    await state.update_data(item_quantities=item_quantities)
    await bot.send_message(message.chat.id, load_text(language, 'add_media'))
    await AdminMenuState.add_media.set()


@dp.message_handler(state=AdminMenuState.add_media, content_types=[types.ContentType.PHOTO, types.ContentType.TEXT, types.ContentType.VIDEO])
async def process_add_media(message: types.Message, state: FSMContext):
    if message.content_type == types.ContentType.VIDEO:
        await process_add_videos(message, state)
    elif message.content_type == types.ContentType.PHOTO:
        await process_add_photos(message, state)
    elif message.content_type == types.ContentType.TEXT:
        if message.text == '/done':
            await process_stop_add_media(message, state)


async def process_add_photos(message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    photo_name = f'{photo_id}.jpg'

    await bot.download_file_by_id(photo_id, get_path_to_media_folder() + photo_name)
    await bot.send_message(message.chat.id, load_text(language, 'successfully_added'))

    data = await state.get_data()
    names_of_medias = data.get('names_of_medias', [])
    names_of_medias.append(photo_name)
    await state.update_data(names_of_medias=names_of_medias)


async def process_add_videos(message, state: FSMContext):
    video_id = message.video.file_id
    video_name = f'{video_id}.mp4'

    await bot.download_file_by_id(video_id, get_path_to_media_folder() + video_name)
    await bot.send_message(message.chat.id, load_text(language, 'successfully_added'))

    data = await state.get_data()
    names_of_medias = data.get('names_of_medias', [])
    names_of_medias.append(video_name)

    await state.update_data(names_of_medias=names_of_medias)


async def process_stop_add_media(message: types.Message, state: FSMContext):
    data = await state.get_data()
    names_of_medias = data.get('names_of_medias', [])
    if len(names_of_medias) == 0:
        await bot.send_message(message.chat.id, load_text(language, 'try_add_media_of_product'))
        return

    await bot.send_message(message.chat.id, load_text(language, 'ask_for_more_variations'))
    await AdminMenuState.add_variants.set()


@dp.message_handler(state=AdminMenuState.add_variants)
async def process_add_variants(message: types.Message, state: FSMContext):
    await save_variant(message, state)

    if message.text.lower() == 'yes':
        await bot.send_message(message.chat.id, load_text(language, 'add_new_varaint_of_product'))
        await bot.send_message(message.chat.id, load_text(language, 'enter_color_product'))
        await AdminMenuState.add_color.set()
    else:
        await bot.send_message(message.chat.id, load_text(language, 'adding_end'))
        await save_product(message, state)


async def save_variant(message: types.Message, state: FSMContext):
    data = await state.get_data()
    item_sizes = data.get('item_sizes')
    item_quantities = data.get('item_quantities')
    item_color = data.get('item_color')
    item_discount = data.get('item_discount')
    variants = data.get('variants', [])

    if len(item_sizes) != len(item_quantities):
        await bot.send_message(message.chat.id, load_text(language, 'error_sizes_quantities'))
        return

    for size, quantity in zip(item_sizes, item_quantities):
        variant = ProductVariant(
            color=item_color,
            sizes=[
                Size(name=size, quantity=quantity)
            ],
            discounts=[
                Discount(value=item_discount)
            ],
        )
        variants.append(variant)

    await state.update_data(variants=variants)


async def get_product_instance(state: FSMContext) -> Product:
    data = await state.get_data()

    product = Product(
        name=data.get('item_name'),
        description=data.get('item_description'),
        price=data.get('item_price'),
        discount=data.get('item_discount'),
        variants=data.get('variants'),
        subcategory_id=data.get('subcategory_id'),
        purchase_price=data.get('item_purchasing_price')
    )

    names_of_medias = data.get('names_of_medias', [])
    folder_name = product.subcategoryId + '_' + product.name

    product.media = save_media_get_links(names_of_medias, folder_name)

    await state.finish()

    return product


async def save_product(message: types.Message, state: FSMContext):
    product = await get_product_instance(state)

    if product is None:
        await bot.send_message(message.chat.id, load_text(language, 'error_all_data_product'))
        await admin_menu(message)
        return

    await PrismaService().create_product(product)

    await bot.send_message(message.chat.id, load_text(language, 'product_added_to_db'))
    await admin_menu(message)


def save_media_get_links(names_of_files, folder_name) -> list:
    array_of_links = []
    for file_name in names_of_files:
        FirebaseStorage().upload_file(file_name, folder_name)
        array_of_links.append(FirebaseStorage().get_link_to_file(file_name, folder_name))
        os.remove(get_path_to_media_folder() + file_name)
    return array_of_links