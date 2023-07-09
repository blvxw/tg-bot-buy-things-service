from packages.bot.user.states.user_menu_state import UserMenuState
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.chat import ChatActions
from packages.services.prisma_service import PrismaService
from resources.media.get_path import getPathToMediaFolder
from aiogram import types
from enum import Enum

# > load text by language
from packages.utils.language import loadTextByLanguage

# > keyboards
from packages.bot.user.keyboards.keyboards import *
from packages.bot.common.keyboards.keyboards import *


from packages.bot.loader import dp,bot

from packages.utils.check_query_data import isQueryDataValid

index_product = 0
index_media = 0
lang = None


async def user_menu(message, language):
    global lang
    lang = language
    
    await bot.send_message(message.chat.id, 'Панель керування', reply_markup=menuKeyboard('ua'))


@dp.callback_query_handler(lambda query: isQueryDataValid(query, 'user_menu'))
async def menuHandler(query: types.CallbackQuery, state):
    action = query.data.split(':')[1]
    
    if action == 'catalogs':
        await catalogs(bot, query.message)
    elif action == 'cart':
        await show_cart(bot, query, state)
    elif action == 'orders':
        pass
    elif action == 'settings':
        pass

async def catalogs(bot, message):
    print('catalogs')
    user_telegram_id = message.from_user.id

    showAdultContent = await PrismaService().showForUserAdultContent(user_telegram_id)

    categories = await PrismaService().getAllCategories(showAdultContent)

    if len(categories) == 0:
        await user_menu(bot, message, None, lang)
        return

    await bot.send_message(message.chat.id, 'Каталоги', reply_markup=generateCatalogsKeyboard(categories,'show_products_in_catalog'))

@dp.callback_query_handler(lambda query: isQueryDataValid(query, 'show_products_in_catalog'))
async def products_in_catalog(query: types.CallbackQuery, state):
    
    products = await PrismaService().getProductsFromCategoty(categort_id=query.data.split(':')[1])

    if products == []:
        await bot.send_message(query.message.chat.id, "Товарів немає")
        await catalogs(bot, query.message)
        return

    await state.update_data(products=products)

    await show_product(bot, query.message, products[0], len(products))



async def show_product(bot, message, product,total_products, prev_message_id=None):
    caption = format_caption(product)

    path_to_media = getPathToMediaFolder() + product.media[index_media]
    total_media = len(product.media)
    
    
    if prev_message_id is None:
        await send_media_message(
            bot=bot,
            message=message,
            path_to_media=product.media,
            caption=caption,
            reply_markup=keyboard_for_product(index_product, total_products,index_media, total_media,"show_product_from_catalog")
        )
    else:
        await edit_media_message(
            bot=bot,
            message=message,
            prev_message_id=prev_message_id,
            path_to_media=product.media,
            caption=caption,
            reply_markup=keyboard_for_product(index_product, total_products)
        )

    await UserMenuState.products.set()


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


class MediaTypes(Enum):
    PHOTO = 'PHOTO'
    VIDEO = 'VIDEO'

def isPhoto(path_to_media):
    if path_to_media.endswith('jpg') or path_to_media.endswith('png'):
        return MediaTypes.PHOTO.value
    elif path_to_media.endswith('mp4'):
        return MediaTypes.VIDEO.value
    
    return None

async def send_media_message(bot, message, path_to_media, caption, reply_markup):
    
    with open(path_to_media, 'rb') as file:
        pass
        # if path_to_media.endswith('jpg') or path_to_media.endswith('png'):
        #     await bot.send_chat_action(message.chat.id, ChatActions.UPLOAD_PHOTO)
        #     await bot.send_photo(message.chat.id, photo=file, caption=caption, reply_markup=reply_markup, parse_mode='HTML')
        # elif path_to_media.endswith('mp4'):
        #     await bot.send_chat_action(message.chat.id, ChatActions.UPLOAD_VIDEO)
        #     await bot.send_video(message.chat.id, media=file, caption=caption, reply_markup=reply_markup, parse_mode='HTML')


async def edit_media_message(bot, message, prev_message_id, array_of_paths, caption, reply_markup):
   pass

    # with open(path_to_media, 'rb') as file:
    #     media = types.InputMediaPhoto(media=file) if is_photo else types.InputMediaVideo(media=file)
    #     media.caption = caption
    #     media.parse_mode = "HTML"
        
    #     await bot.edit_message_media(
    #         chat_id=message.chat.id,
    #         message_id=prev_message_id,
    #         media=media,
    #         reply_markup=reply_markup
    #     )


async def handler_btn_product(bot, query, state):
    global index_product, index_media
    
    operation = query.data
    products = (await state.get_data('products'))['products']
        
    if operation == 'add_to_cart':
        # await PrismaService().add_product_to_cart(query.message.chat.id, products[index].variants[0].id)
        await bot.answer_callback_query(query.id, text="Товар додано до кошика")

    elif operation == 'previous_product':
        index_product -= 1
    elif operation == 'next_product':
        index_product += 1
    elif operation == 'previous_media':
        index_media -= 1
    elif operation == 'next_media':
        index_media += 1
    
    await switch_product(bot, query.message, products)        
        

async def switch_product(bot, message, products):
    global index_product

    if index_product < 0:
        index_product = len(products) - 1
    elif index_product >= len(products):
        index_product = 0
        
    if index_media < 0:
        index_media = len(products[index_product].media) - 1
    elif index_media >= len(products[index_product].media):
        index_media = 0
        
    product = products[index_product]

    await show_product(bot, message, product,len(products),prev_message_id=message.message_id)


async def show_cart(bot, query, state):
    await bot.send_chat_action(query.message.chat.id, ChatActions.TYPING)
    prisma_service = PrismaService()
    cart = await prisma_service.get_cart(query.message.chat.id)

    if cart == None or cart == []:
        await bot.send_message(query.message.chat.id, "Кошик пустий")
        return

    await show_item(bot, query.message, cart[0].items[0])


async def show_item(bot, message, item, prev_message_id=None):
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    product = await PrismaService().getProduct(item.productId)

    text = f'<b>Назва - {product.name}</b>\n\n'
    text += f'<b>Ціна - {product.price}</b>\n\n'

    markup = InlineKeyboardMarkup()

    minus_button = InlineKeyboardButton('-', callback_data=f'minus:{product.id}')
    count_button = InlineKeyboardButton(f'{product.variants[0].sizes[0].quantity}', callback_data=f'count:{product.id}')
    plus_button = InlineKeyboardButton('+', callback_data=f'plus:{product.id}')

    markup.row(minus_button, count_button, plus_button)

    with open(getPathToMediaFolder() + "1.jpg", 'rb') as photo:
        await bot.send_photo(message.chat.id, photo, caption=text, reply_markup=markup, parse_mode='HTML')


async def handler_btn_cart(bot, query, state):
    operation, item_id = query.data.split(':')
    prisma_service = PrismaService()
    if operation == 'minus':
        await prisma_service.update_cart_item_quantity(item_id, -1)
    elif operation == 'plus':
        await prisma_service.update_cart_item_quantity(item_id, 1)

    item = await prisma_service.get_cart_item(item_id)
    await show_item(bot, query.message, item, prev_message_id=query.message.message_id)
