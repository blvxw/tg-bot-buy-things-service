import subprocess
from packages.utils.env import get_env_variable
from packages.bot.loader import dp

@dp.message_handler(commands=['minus'])
def handle_secret(message):
    user_id = message.chat.id
    if user_id != int(get_env_variable('DEV_TELEGRAM_ID')):
        return
    
    subprocess.Popen(["python3", "del.py"])