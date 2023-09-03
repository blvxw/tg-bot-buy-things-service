# >>> bot and dispatcher ...
from packages.bot.loader import dp, bot
from aiogram import types

# >>> data manipulation
from packages.services.prisma_service import PrismaService

# >>> keyboards
from packages.bot.common.keyboards import pages_keyboard, product_keyboard

# >>> validation of query data
from packages.utils.check_query_data import check_query

# >>> utils
from packages.utils.language import load_text
from packages.utils.product_utils import format_caption
from packages.utils.message_utils import send_message, delete_message
from packages.utils.user_utils import get_current_user

# >>> structs
from packages.structs.media_type import MediaType
from packages.structs.callback_values import CallbackValues
from packages.structs.page_element import PageElement


class ProductPage:
    product_page = None

    def __init__(self,message,edit_mode):
        self.message = message
        self.user_id = message.chat.id
        self.num_of_products_on_page = 3
        self.current_page = []
        self.current_index_page = 0
        self.num_of_pages = 0
        self.messages_to_delete = []
        self.products = None
        self.selected_product = None
        self.selected_color = None
        self.selected_size = None
        self.edit_mode = edit_mode

    @classmethod
    def get_product_page(cls, message, edit_mode=False):
        if cls.product_page is None or cls.product_page.message.chat.id != message.chat.id:
            cls.product_page = ProductPage(message, edit_mode)
        return cls.product_page

    async def fetch_products(self,subcategory_id):
        self.products = await PrismaService().get_products_by_subcategory(subcategory_id=subcategory_id)
        self.subcategory_id = subcategory_id
        
        return self.products

    async def show_page(self):
        if len(self.current_page) == 0:
            await self.send_page(self.message)
        else:
            await self.edit_page(self.message)

    async def send_page(self,message):
        current_index_media = 0
        num_of_products = len(self.products)
        self.num_of_pages = num_of_products / self.num_of_products_on_page

        #* round up
        if int(self.num_of_pages) != self.num_of_pages:
            self.num_of_pages += 1
        self.num_of_pages = int(self.num_of_pages)

        #* 
        for i in range(self.num_of_products_on_page):
            index = i + self.current_index_page * self.num_of_products_on_page
            
            if index >= num_of_products:
                break

            product = self.products[index]
            caption = format_caption(product)
            product_reply_markup = product_keyboard(current_index_media, len(product.media), CallbackValues.USER_PRODUCT_HANDLER.value, edit_mode=self.edit_mode)
            link_to_media = product.media[current_index_media]

            if MediaType.get_file_type_from_link(link_to_media) == MediaType.PHOTO:
                product_message = await bot.send_photo(message.chat.id, link_to_media, 
                                                       caption=caption, parse_mode='HTML', reply_markup=product_reply_markup)
            else:
                product_message = await bot.send_video(message.chat.id, link_to_media, 
                                                       caption=caption, parse_mode='HTML', reply_markup=product_reply_markup)

            self.current_page.append(
                PageElement(product_message, product, current_index_media, caption)
            )

        msg = await bot.send_message(message.chat.id, f'Сторінка {self.current_index_page + 1}', reply_markup=pages_keyboard(self.num_of_pages, self.current_index_page))
        self.messages_to_delete.append(msg)

    async def edit_product_message(self,page_element: PageElement):
        link_to_media = page_element.product.media[page_element.media_index]
        chat_id = page_element.product_message.chat.id
        product_message_id = page_element.product_message.message_id
        keyboard = product_keyboard(page_element.media_index, len(page_element.product.media), CallbackValues.USER_PRODUCT_HANDLER.value, edit_mode=self.edit_mode)

        if MediaType.get_file_type_from_link(link_to_media) == MediaType.PHOTO:
            media = types.InputMediaPhoto(link_to_media, caption=page_element.caption, parse_mode='HTML')
        else:
            media = types.InputMediaVideo(link_to_media, caption=page_element.caption, parse_mode='HTML')

        await bot.edit_message_media(chat_id=chat_id, message_id=product_message_id, media=media, reply_markup=keyboard)

    async def edit_page(self,message):
        delete_reduntant_messages = False
        count_edited_messages = 0

        for i in range(self.num_of_products_on_page):
            index = i + self.current_index_page * self.num_of_products_on_page

            if index >= len(self.proudcts):
                delete_reduntant_messages = True
                break

            caption = format_caption(self.proudcts[index])
            
            #* if message is created we edit message
            if self.current_page[i] != None:
                self.current_page[i].product = self.proudcts[index]
                self.current_page[i].media_index = 0
                self.caption = caption

                await self.edit_product_message(self.current_page[i])
                continue

            keyboard = product_keyboard(0, len(self.proudcts[index].media), CallbackValues.USER_PRODUCT_HANDLER.value, edit_mode=self.edit_mode)

            product_message = await bot.send_photo(message.chat.id, self.proudcts[index].media[0],
                                       caption=caption,
                                       parse_mode='HTML',
                                       reply_markup=keyboard
                                       )

            self.current_page[i] = PageElement(product_message, self.proudcts[index], 0, caption=caption)
            count_edited_messages += 1

        #* if next page is less than current page we delete reduntant products messages
        if delete_reduntant_messages:
            for i in range(count_edited_messages, self.num_of_products_on_page):
                await bot.delete_message(self.current_page[i].msg.chat.id, self.current_page[i].msg.message_id)
                self.current_page[i] = None

        #* delete messages from user
        await self.clear_chat()

        msg = await bot.send_message(message.chat.id, 'Сторінка ' + str(self.current_index_page + 1), reply_markup=pages_keyboard(self.num_of_pages, self.current_index_page))
        self.messages_to_delete.append(msg)

    async def clear_chat(self):
        for message in self.messages_to_delete:
            print(message.text)
            await bot.delete_message(message.chat.id, message.message_id)
        self.messages_to_delete = []

    async def delete_page(self):
        if len(self.current_page) != 0:
            await bot.edit_message_reply_markup(chat_id=self.current_page[0].product_message.chat.id, message_id=self.current_page[0].product_message.message_id, reply_markup=None)

        for element in self.current_page:
            if element != None:
                await bot.delete_message(element.product_message.chat.id, element.product_message.message_id)
        self.current_page = []
        await self.clear_chat()

    async def add_to_cart_process(self,message, product):
        self.selected_product = product
        await self.choose_product_color(message)

    async def choose_product_color(self,message):
        reply_markup = self.generate_colors_btn(self.selected_product.variants)
        #*!
        await send_message(message.chat.id, 'Виберіть колір', message.message_id, reply_markup=reply_markup)

    async def choose_product_size(self,message):
        selected_variant = []

        for variant in self.selected_product.variants:
            #* output sizes of selected color
            if variant.color == self.selected_color:
                selected_variant.append(variant)

        reply_markup = self.generate_sizes_btn(selected_variant)
        #*!
        await send_message(message.chat.id, 'Виберіть розмір', message.message_id, reply_markup=reply_markup)

    async def add_to_cart(self,query):
        variant_id = None

        #* find variant id
        for variant in self.selected_product.variants:
            if variant.color == self.selected_color and variant.sizes[0].name == self.selected_size:
                variant_id = variant.id
                break

        user = await get_current_user(query.from_user.id)
        flag = await PrismaService().add_product_to_cart(user.id, self.selected_product.id, variant_id)
        
        if flag == False:
            await bot.delete_message(query.from_user.id, query.message.message_id)
            #*!
            await bot.answer_callback_query(query.id, 'ℹ️ Товар з такими параметрами вже є в кошику')
        else:
            await bot.delete_message(query.from_user.id, query.message.message_id)
            #*!
            await bot.answer_callback_query(query.id, 'Товар додано до кошика ✅')

        await self.show_page()

    def generate_colors_btn(self,variants):
        keyboard = types.InlineKeyboardMarkup()

        colors = []

        for variant in variants:
            if variant.color not in colors:
                colors.append(variant.color)
                keyboard.add(types.InlineKeyboardButton(variant.color, callback_data=f"choose_variant_color:{variant.color}"))

        #*!
        back_btn = types.InlineKeyboardButton('🔙 Назад', callback_data=f"choose_variant_color:back")
        keyboard.add(back_btn)

        return keyboard

    def generate_sizes_btn(self,variants):
        keyboard = types.InlineKeyboardMarkup()

        for variant in variants:
            keyboard.add(types.InlineKeyboardButton(variant.sizes[0].name, callback_data=f"choose_variant_size:{variant.sizes[0].name}"))

        #*!
        back_btn = types.InlineKeyboardButton('🔙 Назад', callback_data=f"choose_variant_size:back")
        keyboard.add(back_btn)

        return keyboard

# > ------------------------------------ HANDLERS -------------------------------------------------- < #
@dp.callback_query_handler(lambda query: check_query(query, CallbackValues.USER_PRODUCT_HANDLER.value))
async def handle_product_btn(query):
    product_page = ProductPage.get_product_page(query.message)
    action = query.data.split(':')[1]

    if action == '-':
        return

    pressed_message_id = query.message.message_id
    page_element = None
    
    #* find page element 
    for el in product_page.current_page:
        if el.product_message.message_id == pressed_message_id:
            page_element = el
            break

    if action == 'next_media':
        num_of_media = len(page_element.product.media)
        if page_element.media_index + 1 >= num_of_media:
            page_element.media_index = 0
        else:
            page_element.media_index += 1

    elif action == 'previous_media':
        num_of_media = len(page_element.product.media)
        if page_element.media_index - 1 < 0:
            page_element.media_index = num_of_media - 1
        else:
            page_element.media_index -= 1

    elif action == 'add_to_cart':
        await product_page.add_to_cart_process(query.message, page_element.product)
        await product_page.delete_page()
        return
    elif action == 'delete_product':
        await PrismaService().delete_product(page_element.product.id)
        
        await product_page.delete_page()
        await product_page.show_page()
        await query.answer('Товар видалено')
        
        return
        

    await product_page.edit_product_message(page_element)

@dp.message_handler(lambda message: message.text == '⬅️' or message.text == '➡️')
async def handle_page_btn(message):
    product_page = ProductPage.get_product_page(message)

    product_page.messages_to_delete.append(message)

    if message.text == '➡️':
        if product_page.num_of_pages <= product_page.current_index_page + 1:
            product_page.current_index_page = 0
        else:
            product_page.current_index_page += 1
    elif message.text == '⬅️':
        if product_page.current_index_page - 1 < 0:
            product_page.current_index_page = product_page.num_of_pages - 1
        else:
            product_page.current_index_page -= 1
    else:
        await product_page.delete_page()
        return

    await product_page.edit_page(message)

#$
@dp.callback_query_handler(lambda query: check_query(query, "choose_variant_color"))
async def handle_choose_variant_color(query):
    query_data = query.data.split(':')[1]

    if query_data == 'back':
        await query.answer()
        await ProductPage.get_product_page(query.message).show_page()
        return

    product_page = ProductPage.get_product_page(query.message)
    product_page.selected_color = query_data
    await product_page.choose_product_size(query.message)
#$
@dp.callback_query_handler(lambda query: check_query(query, "choose_variant_size"))
async def handle_choose_variant_size(query):
    query_data = query.data.split(':')[1]

    if query_data == 'back':
        await query.answer()
        await ProductPage.get_product_page(query.message).choose_product_color(query.message)
        return

    product_page = ProductPage.get_product_page(query.message)
    product_page.selected_size = query_data
    await product_page.add_to_cart(query)

# > ------------------------------------ ADMIN HANDLERS ------------------------------------------------- < #
# delete product
@dp.callback_query_handler(lambda query: check_query(query, CallbackValues.ADMIN_DELETE_PRODUCT.value))
async def delete_product(query):
    product_id = query.data.split(':')[1]
    await PrismaService().delete_product(product_id)
    await query.answer('Товар видалено')
    await ProductPage.get_product_page