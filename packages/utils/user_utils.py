from packages.bot.loader import dp
from packages.services.prisma_service import PrismaService


async def get_current_user(user_telegram_id):
    current_user = None

    try:
        state = dp.current_state(user=user_telegram_id)
        data = await state.get_data()
        current_user = data['current_user']
    except:
        pass

    if current_user is None:
        current_user = await PrismaService().get_user(user_telegram_id)
        await state.update_data(current_user=current_user)

    return current_user


async def get_user_language(user_telegram_id):
    current_user = await get_current_user(user_telegram_id)
    return current_user.language


async def update_current_user(user_telegram_id, current_user):
    state = dp.current_state(user=user_telegram_id)
    await state.update_data(current_user=current_user)
