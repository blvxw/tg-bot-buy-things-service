
async def getMessageFromUser(message):
    return message.text

async def sendQueryAnswer(query,message):
    await query.answer(text=message, show_alert=True)