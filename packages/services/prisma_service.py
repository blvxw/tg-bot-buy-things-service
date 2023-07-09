import prisma
from packages.patterns.singleton import Singleton
from packages.classes.product import Product


class PrismaService(metaclass=Singleton):
    def __init__(self):
        self.prisma = prisma.Prisma()

    async def initialize(self):
        await self.connect()
        print('\033[92m[DB]\033[0m Connected to database')

    async def connect(self):
        await self.prisma.connect()

    async def disconnect(self):
        await self.prisma.disconnect()
        
    async def isAdmin(self, user_telegram_id):
        user = await self.findUserByTelegramId(user_telegram_id)

        if user is None:
            return False

        return user.role == 'ADMIN'
        
    async def isUser(self, user_telegram_id):
        user = await self.findUserByTelegramId(user_telegram_id)

        if user is None:
            return False

        return user.role == 'USER'
    
    async def getCategoryIds(self, name):
        category = await self.prisma.category.find_first(where={'name': name})
        return str(category.id)

    async def getAllCategories(self, adultContent=False):
        if adultContent:
            return await self.prisma.category.find_many()
        
        categories = await self.prisma.category.find_many(
            where={'adultContent': False}
        )

        return categories

      
    async def addProduct(self, product):
        variant_data = []
        for variant in product.variants:
            size_data = [{'name': size.name, 'quantity': size.quantity} for size in variant.sizes]
            discount_data = [{'value': discount.value} for discount in variant.discounts]
            variant_data.append({
                'color': variant.color,
                'sizes': {'create': size_data},
                'discounts': {'create': discount_data}
            })
        product_data = {
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'discount': product.discount,
            'media': product.media,
            'variants': {'create': variant_data}
        }

        await self.prisma.category.update(
            where={'id': product.categoryId},
            data={'products': {'create': [product_data]}}
        )

    async def checkCategoryExists(self, name):
        category = await self.prisma.category.find_first(where={'name': name})

        return category != None

    async def addCategory(self, name, adultContent=False):

        flag = await self.checkCategoryExists(name)

        if flag:
            return False

        await self.prisma.category.create(
            data={
                'name': name,
                'adultContent': adultContent
            }
        )

        return True

    async def setAdultTypeCategory(self, name):
        await self.prisma.category.update(
            where={'name': name},
            data={
                'adultContent': True
            }
        )

    async def showForUserAdultContent(self, user_telegram_id):
        user = await self.findUserByTelegramId(user_telegram_id)

        if user is None:
            return False

        return user.adultContent

    async def addUser(self, user):
        await self.prisma.user.create(
            data={
                'telegram_id': str(user.telegram_id),
                'name': user.name,
                'surname': user.surname,
                'email': user.email,
                'phone': user.phone,
                'language': user.language,
            },
        )

    async def findUserByTelegramId(self, telegram_id):
        user = await self.prisma.user.find_unique(
            where={
                'telegram_id': str(telegram_id)
            })
        return user

    async def isUserLoggedIn(self, telegram_id):
        user = await self.findUserByTelegramId(telegram_id)
        if user is None:
            return False

        return user.login

    async def checkUserExistsColumn(self, column, value):
        user = await self.prisma.user.find_unique(
            where={
                column: value
            })
        return user != None

    async def getLangByTelegramId(self, telegram_id):
        user = await self.findUserByTelegramId(telegram_id)
        return user.language

    async def getProductsFromCategoty(self, categort_id):
        category = await self.prisma.category.find_first(
            where={
                'id': str(categort_id)
            },
            include={
                'products': {
                    'include': {
                        'variants': {
                            'include': {
                                'discounts': True,
                                'sizes': True
                            }
                        }
                    }
                }
            }
        )

        return category.products

    async def add_product_to_cart(self, telegram_id, product_variant_id, quantity=1):
        user = await self.prisma.user.find_unique(where={'telegram_id': str(telegram_id)})
        if user is None:
            return

        product_variant = await self.prisma.productvariant.find_unique(where={"id": product_variant_id})
        if product_variant is None:
            return

        cart = await self.prisma.cart.find_first(where={'userId': user.id})
        if cart is None:
            await self.prisma.cart.create(data={"userId": user.id})

        #!
        # size = 'M'
        # size_variant = await self.prisma.size.find_unique(
        #     where={"name": size, "variantId": product_variant.id}
        # )

        # if size_variant is None:
        #     return

        # cart_item = await self.prisma.cartItem.find_first(
        #     where={"productVariantId": product_variant.id, "sizeId": size_variant.id, "cartId": user.cart}
        # )
        cart_item = None

        if cart_item is None:
            # Додавання нового товару до корзини
            cart_item = await self.prisma.cartitem.create(
                data={
                    "productId": product_variant.productId,
                    "productVariantId": product_variant.id,
                    # "sizeId": size_variant.id,
                    "quantity": quantity,
                    "cartId": cart.id,
                }
            )
        else:
            # Оновлення кількості товару в корзині
            await self.update_cart_item_quantity(cart_item.id, quantity)

        # Повернення оновленої корзини
        cart = await self.prisma.cart.find_unique(where={"id": cart.id}, include={"items": True})
        return cart

    async def update_cart_item_quantity(self, cart_item_id, quantity):
        cart_item = await self.prisma.cartItem.find_unique(where={"id": cart_item_id})
        if cart_item is None:
            return

        updated_quantity = cart_item.quantity + quantity
        if updated_quantity <= 0:
            # Видалення товару з корзини, якщо кількість стає менше або рівно нулю
            await self.prisma.cartItem.delete(where={"id": cart_item_id})
        else:
            # Оновлення кількості товару в корзині
            await self.prisma.cartItem.update(
                where={"id": cart_item_id}, data={"quantity": updated_quantity}
            )

    async def remove_product_from_cart(self, cart_item_id):
        await self.prisma.cartItem.delete(where={"id": cart_item_id})

    async def check_product_availability(self, product_variant_id, size):
        size_variant = await self.prisma.size.find_unique(
            where={"name": size, "variantId": product_variant_id}
        )

        if size_variant is None:
            return False

        if size_variant.quantity <= 0:
            return False

        return True

    async def get_cart(self, telegram_id):
        user = await self.prisma.user.find_unique(where={'telegram_id': str(telegram_id)}, include={'cart': {'include': {'items': True}}})
        print(user)
        if user is None:
            return None

        return user.cart

    async def getProduct(self, product_id):

        product = await self.prisma.product.find_unique(where={'id': str(product_id)}, include={'variants': {'include': {'discounts': True, 'sizes': True}}})

        return product
