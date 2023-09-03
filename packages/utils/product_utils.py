def format_caption(product,product_variant=None):
    caption = f"<b>{product.name}</b>\n\n"
    caption += f"Опис: {product.description}\n\n"
    if product.discount != 0:
        caption += f"Ціна: {product.price - product.discount} \t <s>{product.price}</s>\n\n"
    else:
        caption += f"Ціна: {product.price} грн.\n\n"

    if product_variant is not None:
        caption += f"Колір: {product_variant.color}\n"
        caption += f"Розмір: {product_variant.sizes[0].name}\n\n"
        return caption
    
    colors_and_sizes = {}
    
    for variant in product.variants:
        color = variant.color

        if color not in colors_and_sizes:
            colors_and_sizes[color] = []

        for size in variant.sizes:
            colors_and_sizes[color].append(size.name)

    caption += "<b>Кольори та розміри товару:</b>\n\n"
    for color, sizes in colors_and_sizes.items():
        sizes_str = ", ".join(sizes)
        caption += f"{color}({sizes_str})\n"

    return caption
