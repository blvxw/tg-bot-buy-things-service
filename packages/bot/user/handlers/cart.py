# >>> data manipulation
from packages.services.prisma_service import PrismaService
from packages.services.firebase_storage import FirebaseStorage

# >>> bot stuff
from packages.bot.loader import bot, dp
from aiogram import types

# >>> types
from aiogram.types import InputMediaPhoto, InputMediaVideo
from packages.structs.media_type import MediaType

# >>> keyboards
from packages.bot.user.keyboards.keyboards import cart_menu_keyboard, edit_order_details_buttons
from packages.bot.common.keyboards import cancel_button

# >>> utils
from packages.utils.message_utils import send_message #! use send_message
from packages.utils.product_utils import format_caption
from packages.utils.user_utils import get_current_user,get_user_language
from packages.utils.check_query_data import check_query
from resources.media.get_path import get_path_to_media_folder

# >>> states
from packages.bot.user.states.submit_order_state import SubmitOrderState

# >>> auth
from packages.bot.user.handlers.auth.auth import process_auth

# >>> os
import os

class Cart:
    cart = None

    def __init__(self, message):
        self.user_telgram_id = message.chat.id
        self.state = dp.current_state(user=self.user_telgram_id)
        self.cart_items = []
        self.current_product_index = 0

    @classmethod
    def get_cart(cls, message):
        if cls.cart is None:
            cls.cart = Cart(message)
        return cls.cart

    async def delete_all_products(self,query):
        [self.cart_items.pop() for _ in range(len(self.cart_items))]
        self.current_product_index = 0
        await bot.delete_message(query.message.chat.id, query.message.message_id)
        await bot.answer_callback_query(query.id, "Ваш кошик порожній")
        await PrismaService().clear_cart(self.user.id)

    async def fetch_cart_items(self):
        self.user = await get_current_user(self.user_telgram_id)
        self.cart_items = await PrismaService().get_cart_items(self.user.id)
        await self.state.update_data(cart=self.cart_items)

    @property
    def total_price(self):
        total_price = 0
        for item in self.cart_items:
            total_price += item.product.price * item.quantity
        return total_price

    async def show_product(self, query, edit=False):
        if not self.cart_items:
            await bot.answer_callback_query(query.id, "Ваш кошик порожній")
            return

        product = self.cart_items[self.current_product_index].product
        product_variant = self.cart_items[self.current_product_index].productVariant

        num_of_product = len(self.cart_items)
        quantity = self.cart_items[self.current_product_index].quantity

        user_lang = await get_user_language(query.from_user.id)
        keyboard = cart_menu_keyboard(user_lang,self.current_product_index, num_of_product, quantity, self.total_price)
        caption = format_caption(product,product_variant)
        link = product.media[0]
        file_type = MediaType.get_file_type_from_link(link)

        if edit == False:
            await bot.delete_message(query.message.chat.id, query.message.message_id)
            if file_type == MediaType.PHOTO:
                await bot.send_photo(query.message.chat.id, link, caption=caption, reply_markup=keyboard)
            elif file_type == MediaType.VIDEO:
                await bot.send_video(query.message.chat.id, link, caption=caption, reply_markup=keyboard)
        else:
            if file_type == MediaType.PHOTO:
                link = InputMediaPhoto(link, caption=caption, parse_mode='HTML')
            elif file_type == MediaType.VIDEO:
                link = InputMediaVideo(link, caption=caption, parse_mode='HTML')

            await bot.edit_message_media(media=link, chat_id=query.message.chat.id,
                                         message_id=query.message.message_id, reply_markup=keyboard)

    async def change_product(self, query, next):
        num_of_products = len(self.cart_items)

        if next:
            if self.current_product_index == num_of_products - 1:
                self.current_product_index = 0
            else:
                self.current_product_index += 1
        else:
            if self.current_product_index == 0:
                self.current_product_index = num_of_products - 1
            else:
                self.current_product_index -= 1

        await self.show_product(query, edit=True)

    async def update_quantity(self, query, new_quantity):
        if new_quantity > 0:
            cart_item = self.cart_items[self.current_product_index]
            flag = await PrismaService().change_quantity(cart_item.id, new_quantity)
            if flag == False:
                await query.answer("Це максимальна кількість даного товару")
                return
            
            cart_item.quantity = new_quantity
            await self.show_product(query, edit=True)

    async def delete_product(self, query):
        cart_item = self.cart_items.pop(self.current_product_index)
        await PrismaService().delete_item(cart_item.id)

        if len(self.cart_items) == self.current_product_index:
            self.current_product_index -= 1

        if self.cart_items:
            await self.show_product(query, edit=True)
        else:
            await bot.delete_message(query.message.chat.id, query.message.message_id)
            await bot.answer_callback_query(query.id, "Ваш кошик порожній")

    async def create_order(self, message, address_to_deliver, link_to_prepayment):
        user = await get_current_user(message.from_user.id)

        total_amount = 0

        for cart_item in self.cart_items:
            total_amount += cart_item.quantity * cart_item.product.price

        await PrismaService().create_order(user.id, self.cart_items, total_amount, link_to_prepayment, address_to_deliver)
        await bot.send_message(message.chat.id, "Замовлення створено")
        await self.state.reset_state(with_data=False)

# > ----------------------------------------------------------------------------------------------- < #
@dp.callback_query_handler(lambda query: check_query(query, 'cart_product_btns'))
async def handle_cart_items_btns(query):
    action = query.data.split(':')[1]
    cart = Cart.get_cart(query.message)

    if action == 'next_product':
        await cart.change_product(query, next=True)
    elif action == 'previous_product':
        await cart.change_product(query, next=False)
    elif action == 'plus_product':
        await cart.update_quantity(query, cart.cart_items[cart.current_product_index].quantity + 1)
    elif action == 'minus_product':
        await cart.update_quantity(query, cart.cart_items[cart.current_product_index].quantity - 1)
    elif action == 'delete_product_from_cart':
        await cart.delete_product(query)
    elif action == 'delete_all_products_from_cart':
        await cart.delete_all_products(query)
    elif action == 'submit_order':
        await get_info_for_order(query.message)

@dp.message_handler(state=[SubmitOrderState.prepayment], text="Edit address")
async def get_info_for_order(message):
    flag = await PrismaService().user_has_enter_info(message.chat.id)
    
    if flag == False:
        await bot.send_message(message.chat.id,"Лише зареєстровані користувачі можуть здійснювати замовлення, будь ласка авторизуйтесь")
        await process_auth(message)
        return
    
    await bot.delete_message(message.chat.id, message.message_id)
    lang = await get_user_language(message.chat.id)
    await bot.send_message(message.chat.id, "Введіть адресу доставки", reply_markup=cancel_button(lang))
    await SubmitOrderState().address.set()

@dp.message_handler(state=SubmitOrderState.address)
async def get_user_address(message, state):
    addres = message.text
    await state.update_data(address=addres)
    number_card =  '0000 0000 0000 0000'
    amount_prepayment = 75
    lang = await get_user_language(message.chat.id)

    await bot.send_message(message.chat.id, f"Надішліть скріншот передоплати\nНомер карти: {number_card} \nСума передплати: {amount_prepayment} грн", reply_markup=cancel_button(lang))
    await SubmitOrderState.prepayment.set()

@dp.message_handler(state=SubmitOrderState.prepayment, content_types=[types.ContentType.PHOTO])
async def get_prepayment_photo(message, state):
    photo_id = message.photo[-1].file_id

    photo_name = f'{photo_id}_prepayment.jpg'
    path_to_photo = get_path_to_media_folder() + photo_name
    await bot.download_file_by_id(photo_id, path_to_photo)

    FirebaseStorage().upload_file(photo_name, message.chat.id)
    link = FirebaseStorage().get_link_to_file(photo_name, message.chat.id)
    os.remove(path_to_photo)

    data = await state.get_data()
    address = data.get('address')

    cart = Cart.get_cart(message)
    await cart.create_order(message, address, link)

@dp.message_handler(state=[SubmitOrderState.address, SubmitOrderState.prepayment], text="Cancel")
async def cancel_order(message, state):
    await bot.send_message(message.chat.id, "Оформлення замовлення скасовано", reply_markup=None)
    await state.reset_state(with_data=False)
# > ----------------------------------------------------------------------------------------------- < #
