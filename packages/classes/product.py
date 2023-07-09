class Product:
    def __init__(self, name, description, price, discount, media, variants, nameCategory=None, id=None, categoryId=None):
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.discount = discount
        self.categoryId = categoryId
        self.variants = variants
        self.nameCategory = nameCategory
        self.media = media
