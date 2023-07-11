class Product:
    def __init__(self, name, description, price, discount, variants,media = None, name_category=None, id=None, category_id=None):
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.discount = discount
        self.categoryId = category_id
        self.variants = variants
        self.nameCategory = name_category
        self.media = media
   