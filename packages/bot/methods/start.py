from packages.utils.language import getText

async def start(self,message):
    
    text = await getText(message.chat.id, 'start')
    await self.bot.send_message(message.chat.id,text)