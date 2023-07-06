from packages.bot.user.keyboards.keyboards import menuKeyboard
from packages.bot.user.states.menu import MenuState
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.chat import ChatActions
from packages.services.prisma_service import PrismaService
from resources.media.get_path import getPathToMediaFolder
from aiogram import types

index = 0

async def user_menu(bot,message, state,language):
    await bot.send_message(message.chat.id, 'Панель керування', reply_markup=menuKeyboard('ua'))
    await MenuState.main.set()

async def menuHandler(bot, query, state):
    if query.data == 'catalogs':
        await catalogs(bot, query.message)
    elif query.data == 'cart':
        await show_cart(bot, query, state)


async def catalogs(bot, message):
    prisma_services = PrismaService()

    catalogs = await prisma_services.getAllIdAndNamesCategories()

    keyboard = InlineKeyboardMarkup()
    row_btns = []
    
    for idx, catalog in enumerate(catalogs):
        row_btns.append(InlineKeyboardButton(catalog.name, callback_data=catalog.id))  

        if idx % 2 == 1 or idx == len(catalogs)-1:  
            keyboard.row(*row_btns)
            row_btns = []

    await bot.send_message(message.chat.id, 'Каталоги', reply_markup=keyboard)
    await MenuState.catalogs.set()
    

async def products_in_catalog(bot, query, state):
    prisma_service = PrismaService()
    products = await prisma_service.getProductFromCategoty(categort_id=query.data)
    
    if products == []:
        await bot.send_message(query.message.chat.id, "Товарів немає")
        return
    
    await state.update_data(products=products)
    
    await show_product(bot, query.message, products[0], len(products))
    

async def show_product(bot, message, product, total_products, current_index=0, prev_message_id=None):
    caption = format_caption(product)
    
    path_to_media = getPathToMediaFolder() + product.photos[0]
    
    if prev_message_id is None:
        await send_media_message(
            bot=bot,
            message=message,
            path_to_media=path_to_media,
            caption=caption,
            reply_markup=keyboard_for_product(current_index, total_products)
        )
    else:
        await edit_media_message(
            bot=bot,
            message=message,
            prev_message=prev_message_id,
            path_to_media=path_to_media,
            caption=caption,
            reply_markup=keyboard_for_product(current_index, total_products)
        )

    await MenuState.products.set()

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

def get_media_group_obj(array_of_path, caption):
    media_group = []
    
    for i,path in enumerate(array_of_path):
        media = get_media_obj(
            path_to_media=path,
            caption=caption if i == 0 else ''
        )
        media_group.append(media)

    return media_group
                     
unclosed_media_group = []
      
def get_media_obj(path_to_media, caption):
    global unclosed_media_group
    
    file = open(path_to_media, 'rb')

    unclosed_media_group.append(file)
    
    if path_to_media.endswith('jpg') or path_to_media.endswith('png'):
        media_file = types.InputMediaPhoto(file, caption=caption, parse_mode='HTML')
    elif path_to_media.endswith('mp4'):
        media_file = types.InputMediaVideo(file, caption=caption, parse_mode='HTML')
    
    return media_file

async def send_media_message(bot, message, path_to_media, caption, reply_markup):
    # media = get_media_obj(path_to_media, caption)
    with open(path_to_media, 'rb') as media_file:
        media_bytes = media_file.read()
        
    if isinstance(media_bytes, types.InputMediaPhoto):
        await bot.send_chat_action(message.chat.id, ChatActions.UPLOAD_PHOTO)
        await bot.send_photo(message.chat.id, media_bytes, caption=caption, reply_markup=reply_markup, parse_mode='HTML')
    elif isinstance(media_bytes, types.InputMediaVideo):
        await bot.send_chat_action(message.chat.id, ChatActions.UPLOAD_VIDEO)
        await bot.send_video(message.chat.id, media_bytes, caption=caption, reply_markup=reply_markup, parse_mode='HTML')


async def edit_media_message(bot, message,prev_message, path_to_medias, caption, reply_markup):
    media = get_media_obj(path_to_medias, caption)
    
    await bot.edit_message_media(message.chat.id, prev_message, media, reply_markup=reply_markup, parse_mode='HTML')
    
    for file in unclosed_media_group:
        file.close()


def keyboard_for_product(current_index, total_products):
    keyboard = InlineKeyboardMarkup(row_width=2)

    previous_button = types.InlineKeyboardButton("Назад", callback_data="previous")
    next_button = types.InlineKeyboardButton("Вперед", callback_data="next")
    count_button = types.InlineKeyboardButton(f"{current_index + 1}/{total_products}", callback_data="count")
    
    keyboard.row(previous_button,count_button,next_button)

    add_to_cart_button = types.InlineKeyboardButton(
        "Додати до кошика",
        callback_data=f"add_to_cart:{current_index}"
    )
    keyboard.row(add_to_cart_button)

    return keyboard


async def handler_btn_product(bot, query, state):
    global index
    operation = query.data
    products = await state.get_data('products')
    products = products['products']
    if operation == 'add_to_cart':
        # await PrismaService().add_product_to_cart(query.message.chat.id, products[index].variants[0].id)
        await bot.answer_callback_query(query.id, text="Товар додано до кошика")

    elif operation == 'previous':
        index -= 1
        await switch_product(bot, query.message,products)
    elif operation == 'next':
        index += 1
        await switch_product(bot, query.message,products)

async def switch_product(bot, message,products):
    global index
    
    if index < 0:
        index = len(products) - 1
    elif index >= len(products):
        index = 0
    
    product = products[index]
    
    await show_product(bot, message, product, index, len(products), prev_message_id=message.message_id)

async def show_cart(bot,query,state):
    await bot.send_chat_action(query.message.chat.id, ChatActions.TYPING)
    prisma_service = PrismaService()
    cart = await prisma_service.get_cart(query.message.chat.id)
        
    if cart == None or cart == []:
        await bot.send_message(query.message.chat.id, "Кошик пустий")
        return
   
    await show_item(bot,query.message,cart[0].items[0])

    
async def show_item(bot,message,item,prev_message_id=None):
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    product =  await PrismaService().getProduct(item.productId)

    text = f'<b>Назва - {product.name}</b>\n\n'
    text += f'<b>Ціна - {product.price}</b>\n\n'
    
    markup = InlineKeyboardMarkup()
    
    minus_button = InlineKeyboardButton('-', callback_data=f'minus:{product.id}')
    count_button = InlineKeyboardButton(f'{product.variants[0].sizes[0].quantity}', callback_data=f'count:{product.id}')
    plus_button = InlineKeyboardButton('+', callback_data=f'plus:{product.id}')
    
    markup.row(minus_button, count_button, plus_button)
    
    with open(getPathToMediaFolder() + "1.jpg", 'rb') as photo:
        await bot.send_photo(message.chat.id,photo, caption=text, reply_markup=markup, parse_mode='HTML')
    
async def handler_btn_cart(bot,query,state):
    operation, item_id = query.data.split(':')
    prisma_service = PrismaService()
    if operation == 'minus':
        await prisma_service.update_cart_item_quantity(item_id, -1)
    elif operation == 'plus':
        await prisma_service.update_cart_item_quantity(item_id, 1)

    item = await prisma_service.get_cart_item(item_id)
    await show_item(bot, query.message, item, prev_message_id=query.message.message_id)
