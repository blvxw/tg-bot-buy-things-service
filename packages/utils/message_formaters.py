def format_order_caption(order):
    caption = "\n\n\n"
    caption += f'🛒 Замовлення №{order.id}\n'
    caption += f'📝 Статус: {order.status}\n'
    caption += f'👤 Замовник: {order.user.name} {order.user.surname}\n'
    caption += f'📞 Телефон: {order.user.phone}\n'
    caption += f'💰 Сума: {order.totalAmount} zl.\n'
    caption += f'🏠 Адреса: {order.address}\n'
    caption += f'📦 Товари:\n'

    for item in order.orderItems:
        caption += f'{item.product.name} - {item.quantity} шт.\n'

    if order.comment:
        caption += f'📝 Коментар від адміна: {order.comment}\n'

    return caption