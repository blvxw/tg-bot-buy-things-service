from packages.bot.loader import dp

async def get_message():
    data = await dp.current_state().get_data()
    try:    
        msg = data['message']
        return msg
    except:
        pass
    return None
        
async def send_message(chat_id, text,user_message_num, reply_markup=None,parse_mode=None) -> None:
    message = await get_message()
    
    if message != None:
        if user_message_num != message.message_id:
            try:
                await dp.bot.delete_message(chat_id,message.message_id)
            except:
                pass
            message = None
    
    if message == None:
        
        msg = await dp.bot.send_message(chat_id, text, reply_markup=reply_markup, parse_mode=parse_mode)
        message = msg
        state = dp.current_state(user=chat_id)
        await state.update_data(message=msg)
    else:
        await dp.bot.edit_message_text(text, chat_id,message_id=message.message_id,reply_markup=reply_markup, parse_mode=parse_mode)      
        
async def delete_message() -> None:
    message = await get_message()
    if message != None:
        await dp.bot.delete_message(message.chat.id,message.message_id)
