# > bot and dispatcher ...
from packages.bot.loader import dp, bot
from aiogram import types
#>>> System
import os


# > data manipulation
from packages.services.prisma_service import PrismaService
from packages.services.firebase_storage import FirebaseStorage

# > keyboards
from packages.bot.common.keyboards.keyboards import generate_pages_btns,get_product_keyboard

# > validation of query data
from packages.utils.check_query_data import isQueryDataValid

# > utils
from packages.utils.language import loadTextByLanguage
from packages.utils.prodcut_utils import format_caption

# > data types
from packages.classes.file_type import FileType
from packages.classes.user_callback import UserCallback

# >>> misc
import time


@dp.callback_query_handler(lambda query: isQueryDataValid(query, UserCallback.USER_PRODUCTS_IN_CATALOG.value))
async def products_in_catalog(query: types.CallbackQuery, state):
    products = await PrismaService().getProductsFromCategoty(categort_id=query.data.split(':')[1])

    if len(products) == 0:
        # * translate text
        await bot.send_message(query.message.chat.id, "Товарів немає")
        return
    await state.update_data(products=products)
    await show_page_of_products(query.message, products)

num_of_products_on_page = 5

class PageElement:
    def __init__(self, msg, product, media_index, caption):
        self.msg = msg
        self.media_index = media_index
        self.product = product
        self.caption = caption
        
cur_page = []
current_index_page = 0
pages_btns = None

async def show_page_of_products(message, products,page = 0):
    if len(cur_page) != num_of_products_on_page:
        await show_page(message, products)
    else:
        await change_page(message, products,page)
            
async def show_page(message,products):
    global cur_page

    current_index_media = 0
    
    num_of_products = len(products)
    num_of_pages = num_of_products // num_of_products_on_page
    
    if int(num_of_pages) != num_of_pages:
        num_of_pages += 1
     

    for i in range(num_of_products_on_page):
        index = i + current_index_page * num_of_products_on_page
        if index >= num_of_products:
            break
        
        product = products[index]
        caption = format_caption(product)
        product_reply_markup = get_product_keyboard(product.id,current_index_media,len(product.media),UserCallback.USER_SHOW_PAGE_OF_PRODUCTS.value)
        link = product.media[current_index_media]
        time_send_photo = time.time()

        msg = await bot.send_photo(message.chat.id,link, caption=caption, parse_mode='HTML',reply_markup=product_reply_markup)
        
        cur_page.append(
            PageElement(msg,product,current_index_media,caption)
        )
        
        time_send_photo = time.time() - time_send_photo
        print(f"Time to send media: {time_send_photo}")

async def edit_page_element(page_element: PageElement):    
    link = page_element.product.media[page_element.media_index]
    chat_id = page_element.msg.chat.id
    msg_id = page_element.msg.message_id
    
    if FileType.get_file_type_from_link(link) == FileType.PHOTO:
        media = types.InputMediaPhoto(link, caption=page_element.caption, parse_mode='HTML')
    else:
        media = types.InputMediaVideo(link, caption=page_element.caption, parse_mode='HTML')
    
    await bot.edit_message_media(chat_id=chat_id, message_id=msg_id, media=media, reply_markup=get_product_keyboard(page_element.product.id,page_element.media_index,len(page_element.product.media),UserCallback.USER_SHOW_PAGE_OF_PRODUCTS.value))
                
async def change_page(message, product,page):
    pass

async def delete_products_messages():
    pass
    
@dp.callback_query_handler(lambda query: isQueryDataValid(query, UserCallback.USER_SHOW_PAGE_OF_PRODUCTS.value))
async def handle_product_btn(query):
    global cur_page
    action = query.data.split(':')[1]
    
    if action == '-':
        return
    
    pressed_message_id = query.message.message_id
    page_element = None
    
    for el in cur_page:
        if el.msg.message_id == pressed_message_id:
            page_element = el
            break
    
    if action == 'next_media':
        num_of_media = len(page_element.product.media)
        if page_element.media_index + 1 >= num_of_media:
            page_element.media_index = 0
        else:
            page_element.media_index += 1

        await edit_page_element(page_element)
    elif action == 'previous_media':
        num_of_media = len(page_element.product.media)
        if page_element.media_index - 1 < 0:
            page_element.media_index = num_of_media - 1
        else:
            page_element.media_index -= 1

        await edit_page_element(page_element)
            