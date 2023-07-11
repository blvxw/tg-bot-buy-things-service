
# > system imports
import os

# > data management
from packages.services.prisma_service import PrismaService
from packages.services.firebase_storage import FirebaseStorage

# > classes
from packages.classes.product import Product
from packages.classes.product_variant import ProductVariant
from packages.classes.size import Size
from packages.classes.discount import Discount

# > keyboards
from packages.bot.admin.keyboards.keyboards import adminMenuKeyboard
from packages.bot.common.keyboards.keyboards import *

# > states
from packages.bot.admin.states.admin_menu_state import AdminMenuState

# > Bot
from aiogram import types
from aiogram.dispatcher import FSMContext
from packages.bot.loader import dp, bot

# > path
from resources.media.get_path import getPathToMediaFolder

# >>> utils
from packages.utils.user_utils import *
from packages.utils.check_query_data import isQueryDataValid
from packages.utils.language import loadTextByLanguage

language = None

async def admin_menu(message):
    global language
    language = await get_user_language(message.chat.id)
    
    await bot.send_message(message.chat.id, loadTextByLanguage(language, 'admin_panel'), reply_markup=adminMenuKeyboard(language))

@dp.callback_query_handler(lambda query: isQueryDataValid(query, 'admin_menu'))
async def handle_choose_action(query: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(query.from_user.id, query.message.message_id)

    action = query.data.split(':')[1]

    if action == 'add_category':
        await bot.send_message(query.from_user.id, loadTextByLanguage(language, 'enter_name_category'))
        await AdminMenuState.create_category.set()
    elif action == 'add_product':
        await send_categories(query, state)


@dp.message_handler(state=AdminMenuState.create_category)
async def process_get_name_category(message, state: FSMContext):
    categoryExsist = await PrismaService().checkCategoryExists(name=message.text)

    if categoryExsist:
        await bot.send_message(message.chat.id, loadTextByLanguage(language, 'category_alredy_added'))
        await admin_menu(message, language)
        return

    await state.update_data(category_name=message.text)
    await bot.send_message(message.chat.id, loadTextByLanguage(language, 'is_adult_category'), reply_markup=yesOrNoKeyboard(language))
    await AdminMenuState.isAdultCategory.set()


@dp.callback_query_handler(state=AdminMenuState.isAdultCategory)
async def process_is_adult_category(query, state: FSMContext):
    await bot.delete_message(query.from_user.id, query.message.message_id)

    name_category = (await state.get_data())['category_name']

    await PrismaService().addCategory(name=name_category, adultContent=query.data == 'yes')
    await bot.send_message(query.from_user.id, loadTextByLanguage(language, 'successfully_added'))

    await state.finish()
    await admin_menu(query.message, language)


async def send_categories(callback_query: types.CallbackQuery, state: FSMContext):
    user_telegram_id = callback_query.from_user.id

    show_adult_content = await PrismaService().showForUserAdultContent(user_telegram_id)

    categories = await PrismaService().getAllCategories(show_adult_content)

    if len(categories) == 0:
        await bot.send_message(callback_query.from_user.id, loadTextByLanguage(language, 'category_not_found'))
        await state.finish()
        return
    
    keyboard = generateCatalogsKeyboard(categories, 'choose_category')

    await bot.send_message(callback_query.from_user.id, loadTextByLanguage(language, 'choose_category_product'), reply_markup=keyboard)


@dp.callback_query_handler(lambda query: isQueryDataValid(query, 'choose_category'))
async def process_select_category(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    category_id = callback_query.data.split(':')[1]

    await state.update_data(category_id=category_id)

    await bot.send_message(callback_query.from_user.id, loadTextByLanguage(language, 'enter_data_about_product'))
    await bot.send_message(callback_query.from_user.id, loadTextByLanguage(language, 'enter_name_product'))

    await AdminMenuState.add_name.set()


@dp.message_handler(state=AdminMenuState.add_name)
async def process_add_name(message: types.Message, state: FSMContext):
    item_name = message.text
    await state.update_data(item_name=item_name)
    await bot.send_message(message.chat.id, loadTextByLanguage(language, 'enter_description_product'))
    await AdminMenuState.add_description.set()


@dp.message_handler(state=AdminMenuState.add_description)
async def process_add_description(message: types.Message, state: FSMContext):
    item_description = message.text
    await state.update_data(item_description=item_description)
    await bot.send_message(message.chat.id, loadTextByLanguage(language, 'enter_price_product'))
    await AdminMenuState.add_price.set()


@dp.message_handler(state=AdminMenuState.add_price)
async def process_add_price(message: types.Message, state: FSMContext):
    try:
        item_price = float(message.text)
        await state.update_data(item_price=item_price)
        await bot.send_message(message.chat.id, loadTextByLanguage(language, 'enter_discount_product'))
        await AdminMenuState.add_discount.set()
    except ValueError:
        await bot.send_message(message.chat.id, loadTextByLanguage(language, 'incorrect_price'))


@dp.message_handler(state=AdminMenuState.add_discount)
async def process_add_discount(message: types.Message, state: FSMContext):
    try:
        item_discount = float(message.text)
        await state.update_data(item_discount=item_discount)
        await bot.send_message(message.chat.id, loadTextByLanguage(language, 'enter_color_product'))
        await AdminMenuState.add_color.set()
    except ValueError:
        await bot.send_message(message.chat.id, loadTextByLanguage(language, 'incorrect_discount'))


@dp.message_handler(state=AdminMenuState.add_color)
async def process_add_color(message: types.Message, state: FSMContext):
    item_color = message.text.lower()
    await state.update_data(item_color=item_color)

    await bot.send_message(message.chat.id, loadTextByLanguage(language, 'enter_sizes_product'))
    await AdminMenuState.add_sizes.set()


@dp.message_handler(state=AdminMenuState.add_sizes)
async def process_add_sizes(message: types.Message, state: FSMContext):
    item_sizes = message.text.split(',')
    item_sizes = [size.strip().lower() for size in item_sizes]  # Переводимо розміри до маленьких літер
    await state.update_data(item_sizes=item_sizes)

    await bot.send_message(message.chat.id, loadTextByLanguage(language, 'enter_quantities_product'))
    await AdminMenuState.add_quantities.set()


@dp.message_handler(state=AdminMenuState.add_quantities)
async def process_add_quantities(message: types.Message, state: FSMContext):
    item_quantities = message.text.split(',')
    try:
        item_quantities = [int(quantity.strip()) for quantity in item_quantities]

        data = await state.get_data()
        item_sizes = data.get('item_sizes')

        if len(item_sizes) != len(item_quantities):
            await bot.send_message(message.chat.id, loadTextByLanguage(language, 'error_quntity_sizes'))
            return

    except ValueError:
        await bot.send_message(message.chat.id, loadTextByLanguage(language, 'incorrect_value_must_be_int'))
        return

    await state.update_data(item_quantities=item_quantities)
    await bot.send_message(message.chat.id, loadTextByLanguage(language, 'send_media_of_product'))
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

    await bot.download_file_by_id(photo_id, getPathToMediaFolder() + photo_name)
    await bot.send_message(message.chat.id, loadTextByLanguage(language, 'successfully_added'))

    data = await state.get_data()
    names_of_medias = data.get('names_of_medias', [])
    names_of_medias.append(photo_name)
    await state.update_data(names_of_medias=names_of_medias)


async def process_add_videos(message, state: FSMContext):
    video_id = message.video.file_id
    video_name = f'{video_id}.mp4'

    await bot.download_file_by_id(video_id, getPathToMediaFolder() + video_name)
    await bot.send_message(message.chat.id, loadTextByLanguage(language, 'successfully_added'))

    data = await state.get_data()
    names_of_medias = data.get('names_of_medias', [])
    names_of_medias.append(video_name)

    await state.update_data(names_of_medias=names_of_medias)


async def process_stop_add_media(message: types.Message, state: FSMContext):
    data = await state.get_data()
    names_of_medias = data.get('names_of_medias', [])
    if len(names_of_medias) == 0:
        await bot.send_message(message.chat.id, loadTextByLanguage(language, 'try_add_media_of_product'))
        return

    await bot.send_message(message.chat.id, loadTextByLanguage(language, 'ask_for_more_variations'))
    await AdminMenuState.add_variants.set()

@dp.message_handler(state=AdminMenuState.add_variants)
async def process_add_variants(message: types.Message, state: FSMContext):
    await save_variant(message, state)

    if message.text.lower() == 'yes':
        await bot.send_message(message.chat.id, loadTextByLanguage(language, 'add_new_varaint_of_product'))
        await bot.send_message(message.chat.id, loadTextByLanguage(language, 'enter_color_product'))
        await AdminMenuState.add_color.set()
    else:
        await bot.send_message(message.chat.id, loadTextByLanguage(language, 'adding_end'))
        await save_product(message, state)


async def save_variant(message: types.Message, state: FSMContext):
    data = await state.get_data()
    item_sizes = data.get('item_sizes')
    item_quantities = data.get('item_quantities')
    item_color = data.get('item_color')
    item_discount = data.get('item_discount')
    variants = data.get('variants', [])

    if len(item_sizes) != len(item_quantities):
        await bot.send_message(message.chat.id, loadTextByLanguage(language, 'error_sizes_quantities'))
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
        name= data.get('item_name'),
        description=data.get('item_description'),
        price=data.get('item_price'),
        discount=data.get('item_discount'),
        variants=data.get('variants'),
        category_id=data.get('category_id'),
    )
        
    names_of_medias = data.get('names_of_medias', [])    
    folder_name = product.categoryId + '_' + product.name    
    
    product.media = save_media_get_links(names_of_medias,folder_name)
    
    await state.finish()
    
    return product

    

async def save_product(message: types.Message, state: FSMContext):
    product = await get_product_instance(state)

    if product is None:
        await bot.send_message(message.chat.id, loadTextByLanguage(language, 'error_all_data_product'))
        await admin_menu(message)
        return

    await PrismaService().addProduct(product)
    
    product = await PrismaService().findPrudctByName(product.name)    
    
    await bot.send_message(message.chat.id, loadTextByLanguage(language, 'product_added_to_db'))
    await admin_menu(message)
    

def save_media_get_links(names_of_files,folder_name) -> list:
    array_of_links = []
    for file_name in names_of_files:
        FirebaseStorage().upload_file(file_name,folder_name)
        array_of_links.append(FirebaseStorage().get_link_to_file(file_name,folder_name))
        os.remove(getPathToMediaFolder() + file_name)
    return array_of_links
