class ProductVariant:
    def __init__(self, color, discounts, id=None, sizes=None, productId=None):
        self.id = id
        self.productId = productId
        self.color = color
        self.sizes = sizes
        self.discounts = discounts
