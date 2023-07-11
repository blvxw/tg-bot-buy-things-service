import prisma
from packages.patterns.singleton import Singleton
from packages.classes.product import Product


class PrismaService(metaclass=Singleton):
    def __init__(self):
        self.prisma = prisma.Prisma()

    async def initialize(self):
        await self.prisma.connect()
        print('\033[92m[DB]\033[0m Connected to database')

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
    async def updateUserLanguage(self, user_telegram_id, language):
        await self.prisma.user.update(
            where={'telegram_id': str(user_telegram_id)},
            data={'language': language}
        )

    async def getCategoryIds(self, name):
        category = await self.prisma.category.find_first(where={'name': name})
        return str(category.id)

    async def getAllCategories(self, adult_content: bool = False):
        if adult_content:
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
        
    async def setShowAdultContent(self, user_telegram_id, value: bool):
        await self.prisma.user.update(
            where={'telegram_id': str(user_telegram_id)},
            data={'adultContent': value}
        )
        
    async def findPrudctByName(self,name):
        product = await self.prisma.product.find_first(where={'name': name})
        return product
            

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
        print('1')
        user = await self.prisma.user.find_unique(
            where={
                'telegram_id': str(telegram_id)
            })
        print('2')
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

    async def getProduct(self, product_id):

        product = await self.prisma.product.find_unique(where={'id': str(product_id)}, include={'variants': {'include': {'discounts': True, 'sizes': True}}})

        return product

    
    async def clear_database(self):
        await self.prisma.cartitem.delete_many()
        await self.prisma.cart.delete_many()
        await self.prisma.discount.delete_many()
        await self.prisma.size.delete_many()
        await self.prisma.productvariant.delete_many()
        await self.prisma.product.delete_many()
        await self.prisma.category.delete_many()
        await self.prisma.user.delete_many()

    async def clear_users(self):
        await self.clear_cart_items()
        await self.prisma.cart.delete_many()
        await self.prisma.user.delete_many()
        
    async def clear_categories(self):
        await self.clear_products()
        await self.prisma.category.delete_many()
        
    async def clear_products(self):
        await self.clear_products_variants()
        await self.prisma.product.delete_many()
        
    async def clear_products_variants(self):    
        await self.prisma.size.delete_many()
        await self.prisma.discount.delete_many()
        await self.prisma.productvariant.delete_many()
        
    async def clear_cart_items(self):
        await self.prisma.cartitem.delete_many()

