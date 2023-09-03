# >>> bot
from aiogram import types
from packages.bot.loader import bot,dp

# >>> data manipulation
from packages.services.prisma_service import PrismaService

# >>> structs
from packages.structs.callback_values import CallbackValues

# >>> keyboards
from packages.bot.admin.keyboards.keyboards import active_orders_keyboard,order_status_keyboard

# >>> state
from packages.bot.admin.states.admin_menu_state import AdminMenuState

# >>> utils
from packages.utils.message_formaters import format_order_caption
from packages.utils.check_query_data import check_query
from packages.utils.message_utils import send_message,delete_message
from packages.utils.language import load_text
from packages.utils.user_utils import get_user_language

cur_page = 0
len_of_orders = 0

async def show_active_orders(query: types.CallbackQuery):
    global len_of_orders
    
    active_orders = await PrismaService().get_active_orders()
    
    state = dp.current_state(user=query.from_user.id)
    await state.update_data(active_orders = active_orders)

    len_of_orders = len(active_orders)
    language = await get_user_language(query.from_user.id)
    if len_of_orders == 0:
        await query.answer(load_text(language,'no_active_orders'))
        return

    await delete_message()
    await bot.send_photo(query.from_user.id,
                        photo=active_orders[0].prepayment_photo,
                        caption=format_order_caption(active_orders[cur_page]),
                        reply_markup=active_orders_keyboard(cur_page,len_of_orders))

@dp.callback_query_handler(lambda query: check_query(query, CallbackValues.ADMIN_ORDERS_MENU_HANDLER.value))
async def handle_order_buttons(query: types.CallbackQuery):
    global cur_page
    action = query.data.split(':')[1]

    if action == CallbackValues.PREVIOUS_ORDER.value:
        await change_page_of_orders(query,False)
    elif action == CallbackValues.NEXT_ORDER.value:
        await change_page_of_orders(query,True)

async def change_page_of_orders(query,is_next):
    global cur_page

    state = dp.current_state(user=query.from_user.id)
    data = await state.get_data()
    active_orders = data.get('active_orders')
    
    if is_next:
        if cur_page == len_of_orders - 1:
            cur_page = 0
        else:
            cur_page += 1
    else:
        if cur_page == 0:
            cur_page = len_of_orders - 1
        else:
            cur_page -= 1

    order = active_orders[cur_page]
    
    await bot.edit_message_media(
        media=types.InputMediaPhoto(order.prepayment_photo),
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
        reply_markup=active_orders_keyboard(cur_page,len_of_orders)
    )

@dp.callback_query_handler(lambda query: check_query(query, CallbackValues.CHANGE_ORDER_STATUS.value))
async def change_order_status(query: types.CallbackQuery):
    state = dp.current_state(user=query.from_user.id)
    data = await state.get_data()
    active_orders = data.get('active_orders')
    cur_order_status = active_orders[cur_page].status
    lang = await get_user_language(query.from_user.id)
    await send_message(query.from_user.id,load_text(lang,'choose_status_order'),query.message.message_id,reply_markup=order_status_keyboard(cur_order_status))

@dp.callback_query_handler(lambda query: check_query(query, CallbackValues.SET_ORDER_STATUS.value))
async def handle_order_status_buttons(query: types.CallbackQuery):
    order_status = query.data.split(':')[1]

    lang = await get_user_language(query.from_user.id)
    await query.answer(f'{load_text(lang,"status_changed_to")} {order_status}')
    
    state = dp.current_state(user=query.from_user.id)
    data = await state.get_data()
    active_orders = data.get('active_orders')
    
    active_orders[cur_page].status = order_status
    
    await state.update_data(active_orders = active_orders)
    
    await change_order_status(query)

    await PrismaService().update_order_status(active_orders[cur_page].id,order_status)

@dp.callback_query_handler(lambda query: check_query(query, CallbackValues.CHANGE_ORDER_COMMENT.value))
async def change_order_comment(query: types.CallbackQuery):
    lang = await get_user_language(query.from_user.id)
    await send_message(query.from_user.id,load_text(lang,"enter_comment_to_order"),query.message.message_id)
    await AdminMenuState.change_comment_to_order.set()

@dp.message_handler(state=AdminMenuState.change_comment_to_order)
async def handle_order_comment(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    data = await state.get_data()
    active_orders = data.get('active_orders')

    active_orders[cur_page].comment = message.text
    
    await state.update_data(active_orders = active_orders)
    
    await PrismaService().update_order_comment(active_orders[cur_page].id,message.text)
    lang = await get_user_language(message.from_user.id)
    await send_message(message.from_user.id,load_text(lang,"comment_changed"),message.message_id)
    await show_active_orders(message)
    await state.finish()