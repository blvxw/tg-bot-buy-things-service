from resources.media.get_path import getPathToMediaFolder
from aiogram import types

# > data manipulation
from packages.services.prisma_service import PrismaService
from packages.services.firebase_storage import FirebaseStorage

# > load text by language
from packages.utils.language import loadTextByLanguage

# > keyboards
from packages.bot.user.keyboards.keyboards import *
from packages.bot.common.keyboards.keyboards import *
 
# >
from packages.classes.file_type import FileType

from packages.utils.check_query_data import isQueryDataValid

from packages.bot.loader import dp, bot



page = 0
lang = None


async def user_menu(message, language):
    global lang
    if lang != language:
        lang = language

    await bot.send_message(message.chat.id, 'Панель керування', reply_markup=menuKeyboard('ua'))


@dp.callback_query_handler(lambda query: isQueryDataValid(query, 'user_menu'))
async def menuHandler(query: types.CallbackQuery, state):
    action = query.data.split(':')[1]

    if action == 'catalogs':
        await catalogs(bot, query.message)
    elif action == 'cart':
        pass
        # await show_cart(bot, query, state)
    elif action == 'orders':
        pass
    elif action == 'settings':
        pass


async def catalogs(bot, message):
    user_telegram_id = message.from_user.id

    showAdultContent = await PrismaService().showForUserAdultContent(user_telegram_id)

    categories = await PrismaService().getAllCategories(showAdultContent)

    if len(categories) == 0:
        await user_menu(bot, message, None, lang)
        return

    await bot.send_message(message.chat.id, 'Каталоги', reply_markup=generateCatalogsKeyboard(categories, 'show_products_in_catalog'))


@dp.callback_query_handler(lambda query: isQueryDataValid(query, 'show_products_in_catalog'))
async def products_in_catalog(query: types.CallbackQuery, state):

    products = await PrismaService().getProductsFromCategoty(categort_id=query.data.split(':')[1])

    if len(products) == 0:
        # > translate text
        await bot.send_message(query.message.chat.id, "Товарів немає")
        await catalogs(bot, query.message)
        return

    await state.update_data(products=products)

    await show_page_of_products(query.message, products)

array_of_msg = []
num_of_products_on_page = 5

async def show_page_of_products(message, products, page=0):
    global array_of_msg
    num_of_products = len(products)

    num_of_pages = num_of_products // num_of_products_on_page

    if int(num_of_pages) != num_of_pages:
        num_of_pages += 1

    print(num_of_pages)

    for i in range(num_of_products_on_page):
        index = i + page * num_of_products_on_page
        if index >= num_of_products:
            break
        used_files = []
        product = products[index]
        caption = format_caption(product)
        media_group = []

        for i, media_name in enumerate(product.media):
            FirebaseStorage().download_file(media_name,products[index].id)
            file = open(getPathToMediaFolder() + media_name, 'rb')
            used_files.append(file)
            if FileType.get_file_type(media_name) == FileType.PHOTO:
                media_group.append(types.InputMediaPhoto(file, caption=caption if i == 0 else '', parse_mode='HTML'))
            elif FileType.get_file_type(media_name) == FileType.VIDEO:
                media_group.append(types.InputMediaVideo(file, caption=caption if i == 0 else '', parse_mode='HTML'))

        cur_message = await bot.send_media_group(message.chat.id, media_group)
        if num_of_pages > 1:
            await bot.send_message(message.chat.id, "Оберіть сторінку", reply_markup=generate_pages_btns(num_of_pages, page, 'btns_pages_products_in_catalog'))
        array_of_msg.append(cur_message)
        import os
        
        for file in used_files:
            file.close()
            os.remove(file.name)    
        

def format_caption(product):
    caption = f"<b>{product.name}</b>\n\n"
    caption += f"Опис: {product.description}\n\n"
    if product.discount != 0:
        caption += f"Ціна: {product.price - product.discount} \t <s>{product.price}</s>\n\n"
    else:
        caption += f"Ціна: {product.price} грн.\n\n"

    colors_and_sizes = {}

    for variant in product.variants:
        color = variant.color

        if color not in colors_and_sizes:
            colors_and_sizes[color] = []

        for size in variant.sizes:
            colors_and_sizes[color].append(size.name)

    caption += "<b>Кольори та розміри товару:</b>\n\n"
    for color, sizes in colors_and_sizes.items():
        sizes_str = ", ".join(sizes)
        caption += f"{color}({sizes_str})\n"

    return caption


async def switch_product(message, products):
    pass

# async def show_cart(bot, query, state):
#     await bot.send_chat_action(query.message.chat.id, ChatActions.TYPING)
#     prisma_service = PrismaService()
#     cart = await prisma_service.get_cart(query.message.chat.id)

#     if cart == None or cart == []:
#         await bot.send_message(query.message.chat.id, "Кошик пустий")
#         return

#     await show_item(bot, query.message, cart[0].items[0])


# async def show_item(bot, message, item, prev_message_id=None):
#     await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
#     product = await PrismaService().getProduct(item.productId)

#     text = f'<b>Назва - {product.name}</b>\n\n'
#     text += f'<b>Ціна - {product.price}</b>\n\n'

#     markup = InlineKeyboardMarkup()

#     minus_button = InlineKeyboardButton('-', callback_data=f'minus:{product.id}')
#     count_button = InlineKeyboardButton(f'{product.variants[0].sizes[0].quantity}', callback_data=f'count:{product.id}')
#     plus_button = InlineKeyboardButton('+', callback_data=f'plus:{product.id}')

#     markup.row(minus_button, count_button, plus_button)

#     with open(getPathToMediaFolder() + "1.jpg", 'rb') as photo:
#         await bot.send_photo(message.chat.id, photo, caption=text, reply_markup=markup, parse_mode='HTML')


# async def handler_btn_cart(bot, query, state):
#     operation, item_id = query.data.split(':')
#     prisma_service = PrismaService()
#     if operation == 'minus':
#         await prisma_service.update_cart_item_quantity(item_id, -1)
#     elif operation == 'plus':
#         await prisma_service.update_cart_item_quantity(item_id, 1)

#     item = await prisma_service.get_cart_item(item_id)
#     await show_item(bot, query.message, item, prev_message_id=query.message.message_id)
