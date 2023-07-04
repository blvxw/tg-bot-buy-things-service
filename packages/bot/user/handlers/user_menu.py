from packages.bot.user.keyboards.keyboards import menuKeyboard
from packages.bot.user.states.menu import MenuState
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.chat import ChatActions
from packages.services.prisma_service import PrismaService
from resources.images.get_path import getPathToPhotoFolder
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
    photo = getPathToPhotoFolder() + products[0].photos[0]
    prev_message = None
    with open(photo, 'rb') as photo_file:
        prev_message = await bot.send_photo(query.message.chat.id, photo_file, caption="test", reply_markup=keyboard_for_product(0, len(products)))
    
    await show_product(bot, query.message, products[0], 0, len(products), prev_message.message_id)
    

async def show_product(bot, message, product, current_index, total_products, prev_message_id=None):
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    # вивести інформацію про товар(назва, ціна, опис,знижка якщо є, кольори, розміри,кількості і т.д.)
    
    text = f"<b>{product.name}</b>\n\n"
    text += f"Опис: {product.description}\n\n"
    if product.discount != 0:
        # виведи закреслену ціну і ціну зі знижкою
        text += f"Ціна: <s>{product.price}</s> \t{product.price - product.discount} грн.\n\n"
    else: 
        text += f"Ціна: {product.price} грн.\n\n"
   
    colors_and_sizes = {}

    # Отримання кольорів та розмірів товару
    
    for variant in product.variants:
        color = variant.color
        
        if color not in colors_and_sizes:
            colors_and_sizes[color] = []
        
        for size in variant.sizes:
            colors_and_sizes[color].append(size.name)

    text += "<b>Кольори та розміри товару:</b>\n\n"
    for color, sizes in colors_and_sizes.items():
        sizes_str = ", ".join(sizes)
        text += f"{color}({sizes_str})\n"

  
    photo = product.photos[0]
    
    with open(getPathToPhotoFolder() + photo, 'rb') as photo_file:
        try:
            await bot.edit_message_media(
                chat_id=message.chat.id,
                message_id=prev_message_id,
                media=types.InputMediaPhoto(media=photo_file, caption=text, parse_mode="HTML"),
                reply_markup=keyboard_for_product(current_index, total_products)
            )
        except Exception as e:
            print(e)

    await MenuState.products.set()


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
    
    with open(getPathToPhotoFolder() + "1.jpg", 'rb') as photo:
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
