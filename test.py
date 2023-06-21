from packages.services.prisma_service import PrismaService
import threading
import asyncio
import time

# Спільна змінна для зберігання загальної кількості підключень
total_connections = 0
lock = threading.Lock()

async def connect_forever():
    global total_connections  # Використовуємо глобальну змінну
    i = 1
    while True:
        time_start = time.time()
        prisma_service = PrismaService()
        await prisma_service.initialize()
        thread_name = threading.current_thread().name
        task_name = asyncio.current_task().get_name()
        
        with lock:
            total_connections += 1  # Збільшуємо загальну кількість підключень в критичній секції
        print(f"Total connections: {total_connections}")

        i += 1

async def main():
    tasks = []
    for i in range(20):
        thread_name = f"Thread-{i+1}"
        task = asyncio.create_task(connect_forever())
        task.set_name(thread_name)
        setattr(task, '_name', thread_name)  # Встановлення імені задачі напряму
        tasks.append(task)

    # Очікування завершення всіх задач
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())
