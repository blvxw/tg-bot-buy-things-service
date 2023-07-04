
#> db
from packages.services.prisma_service import PrismaService

#> classes
from packages.classes.product import Product
from packages.classes.product_variant import ProductVariant
from packages.classes.size import Size
from packages.classes.discount import Discount

#> loader text
from packages.utils.language import *

#> keyboards
from packages.bot.admin.keyboards.keyboards import adminMenuKeyboard

#> states
from packages.bot.admin.states.admin_state import AdminState

#> misc
from aiogram import types
from aiogram.dispatcher import FSMContext

from resources.images.get_path import getPathToPhotoFolder

lang = 'en'

async def admin_menu(bot,message,state,language):
    global lang
    lang = language
    
    await bot.send_message(message.chat.id, loadTextByLanguage(lang,'admin_panel'), reply_markup=adminMenuKeyboard(lang))
    await AdminState.choose_action.set()

async def handle_choose_action(bot,query: types.CallbackQuery, state: FSMContext):
    action = query.data.split(":")[1]
    tmp = query.data.split(":")[0]
    
    if tmp != "action":
        await bot.delete_message(query.from_user.id, query.message.message_id)
        return
    
    if action == "add_category":
        await bot.send_message(query.from_user.id, loadTextByLanguage(lang,'enter_name_category'))
        await AdminState.create_category.set()
    elif action == "add_product":
        await send_categories(bot,query,state)
        
    
async def handle_create_category(bot,message, state: FSMContext):
    flag = await PrismaService().addCategory(name = message.text)
    
    if flag == False: 
        await bot.send_message(message.chat.id, loadTextByLanguage(lang,'category_alredy_added'))
    else: 
        await bot.send_message(message.chat.id, loadTextByLanguage(lang,'category_added'))
    
    await admin_menu(bot,message,state,lang)

async def send_categories(bot,callback_query: types.CallbackQuery, state: FSMContext):
    categories = await PrismaService().getAllIdAndNamesCategories()
    
    if len(categories) == 0:
        await bot.send_message(callback_query.from_user.id, loadTextByLanguage(lang,'category_not_found'))
        return
    
    keyboard = types.InlineKeyboardMarkup()

    for category in categories:
        select_category_button = types.InlineKeyboardButton(text = category.name, callback_data=f"select_category:{category.id}")
        keyboard.row(select_category_button)

    await bot.send_message(callback_query.from_user.id, loadTextByLanguage(lang,'choose_category_product'), reply_markup=keyboard)
    await AdminState.choose_category.set()

async def handle_select_category(bot,callback_query: types.CallbackQuery, state: FSMContext):
    category_id = callback_query.data.split(":")[1]
    tmp = callback_query.data.split(":")[0]
    
    if tmp != "select_category":
        await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
        return

    await state.update_data(category_id=category_id)
    await bot.send_message(callback_query.from_user.id, loadTextByLanguage(lang,'enter_data_about_product'))
    await bot.send_message(callback_query.from_user.id, loadTextByLanguage(lang,'enter_name_product'))
    await AdminState.add_name.set()


async def handle_add_name(bot,message: types.Message, state: FSMContext):
    item_name = message.text
    await state.update_data(item_name=item_name)
    await bot.send_message(message.chat.id, loadTextByLanguage(lang,'enter_description_product'))
    await AdminState.add_description.set()

async def handle_add_description(bot,message: types.Message, state: FSMContext):
    item_description = message.text
    await state.update_data(item_description=item_description)
    await bot.send_message(message.chat.id, loadTextByLanguage(lang,'enter_price_product'))
    await AdminState.add_price.set()

async def handle_add_price(bot,message: types.Message, state: FSMContext):
    try:
        item_price = float(message.text)
        await state.update_data(item_price=item_price)
        await bot.send_message(message.chat.id, loadTextByLanguage(lang,'enter_discount_product'))
        await AdminState.add_discount.set()
    except ValueError:
        await bot.send_message(message.chat.id, loadTextByLanguage(lang,'incorrect_price'))

async def handle_add_discount(bot,message: types.Message, state: FSMContext):
    try:
        item_discount = float(message.text)
        await state.update_data(item_discount=item_discount)
        await bot.send_message(message.chat.id, loadTextByLanguage(lang,'enter_color_product'))
        await AdminState.add_color.set()
    except ValueError:
        await bot.send_message(message.chat.id, loadTextByLanguage(lang,'incorrect_discount'))

async def handle_add_color(bot,message: types.Message, state: FSMContext):
    item_color = message.text.lower()  # Переводимо колір до маленьких літер
    await state.update_data(item_color=item_color)
    await bot.send_message(message.chat.id, loadTextByLanguage(lang,'enter_sizes_product'))
    await AdminState.add_sizes.set()

async def handle_add_sizes(bot,message: types.Message, state: FSMContext):
    item_sizes = message.text.split(",")
    item_sizes = [size.strip().lower() for size in item_sizes]  # Переводимо розміри до маленьких літер
    await state.update_data(item_sizes=item_sizes)
    await bot.send_message(message.chat.id, loadTextByLanguage(lang,'enter_quantities_product'))
    await AdminState.add_quantities.set()

async def handle_add_quantities(bot,message: types.Message, state: FSMContext):
    item_quantities = message.text.split(",")
    item_quantities = [int(quantity.strip()) for quantity in item_quantities]
    await state.update_data(item_quantities=item_quantities)
    await bot.send_message(message.chat.id, loadTextByLanguage(lang,'send_photo_product'))
    await AdminState.add_photos.set()

async def handle_add_photos(bot,message, state: FSMContext):    
    photo = message.photo[-1]  # Беремо лише останню (найбільшу) фотографію
    photo_name = f"{photo.file_id}.jpg"
    await bot.download_file_by_id(photo.file_id, getPathToPhotoFolder() + photo_name)
    await bot.send_message(message.chat.id, loadTextByLanguage(lang,'photo_successfully_added'))

    data = await state.get_data()
    item_photos = data.get('item_photos', [])
    item_photos.append(photo_name)
    await state.update_data(item_photos=item_photos)
    

async def handle_add_done(bot,message: types.Message, state: FSMContext):
    await bot.send_message(message.chat.id,loadTextByLanguage(lang,'ask_for_more_variations'))
    await AdminState.add_variants.set()

async def handle_add_variants(bot,message: types.Message, state: FSMContext):
    await save_variant(bot,message, state)   
    
    if message.text.lower() == 'yes':
        await bot.send_message(message.chat.id, loadTextByLanguage(lang,'add_new_varaint_of_product'))
        await bot.send_message(message.chat.id, loadTextByLanguage(lang,'enter_color_product'))
        await AdminState.add_color.set()
    else:
        await bot.send_message(message.chat.id, loadTextByLanguage(lang,'adding_end'))
        await save_product(bot,message, state)

async def save_variant(bot,message: types.Message, state: FSMContext):
    data = await state.get_data()
    item_sizes = data.get('item_sizes')
    item_quantities = data.get('item_quantities')
    item_color = data.get('item_color')
    print('item_color',item_color)
    item_discount = data.get('item_discount')
    variants = data.get('variants', [])

    if len(item_sizes) != len(item_quantities):
        await bot.send_message(message.chat.id, loadTextByLanguage(lang,'error_sizes_quantities'))
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

    for variant in variants:
        print(variant.color)
    await state.update_data(variants=variants)


async def save_product(bot,message: types.Message, state: FSMContext):
    data = await state.get_data()

    item_name = data.get('item_name')
    item_description = data.get('item_description')
    item_price = data.get('item_price')
    item_discount = data.get('item_discount')
    category_id = data.get('category_id')
    item_photos = data.get('item_photos')
    variants = data.get('variants')

    await state.finish()

    if not variants or not item_photos or not item_description or not item_name or not item_price or item_discount is None or not category_id:
        await bot.send_message(message.chat.id, loadTextByLanguage(lang,'error_all_data_product'))
        return


    product = Product(
        name=item_name,
        description=item_description,
        price=item_price,
        discount=item_discount,
        variants=variants,
        categoryId=category_id,
        photos=item_photos
    )

    await PrismaService().addProduct(product)
   
    await bot.send_message(message.chat.id, loadTextByLanguage(lang,'product_added_to_db'))
