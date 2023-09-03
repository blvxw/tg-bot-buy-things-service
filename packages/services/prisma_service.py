import prisma
from packages.patterns.singleton import Singleton

class PrismaService(metaclass=Singleton):
    def __init__(self):
        self.prisma = prisma.Prisma()

    # ? CONNECTION METHODS
    async def initialize(self):
        await self.prisma.connect()
        print('\033[92m[DB]\033[0m Connected to database')

    async def disconnect(self):
        await self.prisma.disconnect()

    # ? USER RELATED METHODS
    async def is_admin(self, user_telegram_id):
        user = await self.get_user(user_telegram_id)

        if user is None:
            return False

        return user.role == 'ADMIN'

    async def is_user(self, user_telegram_id):
        user = await self.get_user(user_telegram_id)

        if user is None:
            return False

        return user.role == 'USER'

    async def change_user_role(self, user_telegram_id, role):
        res = await self.prisma.user.update(
            where={'telegram_id': str(user_telegram_id)},
            data={'role': role}
        )

        print(res)

    async def set_user_language(self, user_telegram_id, language):
        await self.prisma.user.update(
            where={'telegram_id': str(user_telegram_id)},
            data={'language': language}
        )

    async def set_show_adult_content(self, user_telegram_id, value: bool):
        await self.prisma.user.update(
            where={'telegram_id': str(user_telegram_id)},
            data={'adultContent': value}
        )

    async def show_for_user_adult_content(self, user_telegram_id,value: bool):
        await self.prisma.user.update(
            where={'telegram_id': str(user_telegram_id)},
            data={'adultContent': value}
        )

    async def add_info_about_user(self, user):
        user = await self.prisma.user.update(
            where={'telegram_id': str(user.telegram_id)},
            data={
                'name': user.name,
                'surname': user.surname,
                'phone': user.phone,
                'email': user.email,
                'language': user.language
            }
        )

    async def set_min_user_info(self, user_telegram_id, language):
        await self.prisma.user.create(
            data={
                'telegram_id': str(user_telegram_id),
                'language': language
            }
        )

    async def get_user(self, telegram_id):
        print('1')
        user = await self.prisma.user.find_unique(
            where={
                'telegram_id': str(telegram_id)
            })
        print('2')
        return user

    async def user_has_enter_info(self, user_telegram_id):
        user = await self.get_user(user_telegram_id)

        flag = user.name != None and user.surname != None and user.email != None and user.phone != None and user.language != None and user.adultContent != None and user.role != None and user.telegram_id != None

        return flag

    async def check_user_exists_column(self, column, value):
        user = await self.prisma.user.find_unique(
            where={
                column: value
            })
        return user != None

    async def user_alredy_send_question(self, user_telegram_id):
        res = await self.prisma.question.find_first(where={'user_telegram_id': str(user_telegram_id)})
        
        return res != None

    # ? QUESTION RELATED METHODS
    async def send_question(self, user_telegram_id, question: str) -> None:
        await self.prisma.question.create(
            data={
                'question': question,
                'user_telegram_id': str(user_telegram_id)
            }
        )
    async def get_question(self, question_id):
        return await self.prisma.question.find_first(where={'id': question_id})
    
    async def get_questions(self) -> list:
        return await self.prisma.question.find_many()

    async def delete_question(self, question_id: int) -> None:
        await self.prisma.question.delete(where={'id': question_id})
    # ? CATEGORY RELATED METHODS
    async def get_categories(self, adultContent=False):
        if adultContent:
            return await self.prisma.category.find_many()
        return await self.prisma.category.find_many(where={'adultContent': False})
    
    async def get_category(self, category_id):
        return await self.prisma.category.find_first(where={'id': category_id})
    
    async def check_category_exists(self, name: str):
        category = await self.prisma.category.find_first(where={'name': name})
        return category != None
    
    async def create_category(self, name, adultContent=False):
        flag = await self.check_category_exists(name)

        if flag:
            return False

        await self.prisma.category.create(
            data={
                 'name': name,
                 'adultContent': adultContent
            }
        )

        return True

    # ? SUBCATEGORY RELATED METHODS
    async def get_subcategories(self, category_id: str):
        return await self.prisma.subcategory.find_many(where={'categoryId': category_id})

    async def get_subcategory(self, subcategory_id):
        return await self.prisma.subcategory.find_first(where={'id': subcategory_id})

    async def check_subcategory_exists(self, name: str):
        subcategory = await self.prisma.subcategory.find_first(where={'name': name})

        return subcategory != None

    async def create_subcategory(self, name,parent_category_id):
        flag = await self.check_subcategory_exists(name)
        print(parent_category_id)

        if flag:
            return False
        
        await self.prisma.category.update(
            where={'id': parent_category_id},
            data={
                'subCategories': {
                    'create': [{
                        'name': name
                    }]
                }
            }
        )

        return True

    # ? PRODUCT RELATED METHODS
    async def create_product(self, product):
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
            'variants': {'create': variant_data},
            'purchasePrice': product.purschasePrice
        }

        await self.prisma.subcategory.update(
            where={'id': product.subcategoryId},
            data={'products': {'create': [product_data]}}
        )

    async def delete_product(self, product_id):
        #* del sizes -> del discount -> del variants ->  del product
        product = await self.prisma.product.find_first(where={'id': product_id}, include={'variants': {'include': {'sizes': True, 'discounts': True}}})

        for variant in product.variants:
            for size in variant.sizes:
                await self.prisma.size.delete(where={'id': size.id})
            for discount in variant.discounts:
                await self.prisma.discount.delete(where={'id': discount.id})
            await self.prisma.productvariant.delete(where={'id': variant.id})

        await self.prisma.product.delete(where={'id': product_id})

    async def get_products_by_subcategory(self, subcategory_id):

        products = await self.prisma.product.find_many(
            where={
                'subcategoryId': subcategory_id,
                'variants': {
                    'some': {
                        'sizes': {
                            'some': {
                                'quantity': {
                                    'gt': 0
                                }
                            }
                        }
                    }
                }
            },
            include={
                'variants': {
                    'include': {
                        'discounts': True,
                        'sizes': True
                    }
                }
            }
        )
        return products

    # ? CART RELATED METHODS
    async def create_cart(self, user_id):
        await self.prisma.cart.create(
            data={
                'userId': user_id
            }
        )

    async def add_product_to_cart(self, user_id, product_id, variant_id, quantity=1) -> bool:

        user_cart = await self.prisma.cart.find_first(where={'userId': user_id}, include={'cartItems': True})

        if user_cart == None:
            await self.create_cart(user_id)
            user_cart = await self.prisma.cart.find_first(where={'userId': user_id}, include={'cartItems': True})

        for item in user_cart.cartItems:
            if item.productVariantId == variant_id:
                return False

        cart = await self.prisma.cart.find_first(where={'userId': user_id})
        await self.prisma.item.create(
            data={
                'productId': product_id,
                'productVariantId': variant_id,
                'quantity': quantity,
                'cartId': cart.id
            }
        )

        return True

    async def change_quantity(self, item_id, quantity):
        item = await self.prisma.item.find_first(where={'id': item_id}, include={'productVariant': {'include': {'sizes': True}}})

        if item.productVariant.sizes[0].quantity < quantity:
            return False

        await self.prisma.item.update(
            where={'id': item_id},
            data={'quantity': quantity}
        )

        return True

    async def get_cart_items(self, user_id):
        cart = await self.prisma.cart.find_first(where={'userId': user_id}, include={'cartItems': {'include': {'product': True, 'productVariant': {'include': {'discounts': False, 'sizes': True}}}}})

        if cart == None:
            return []

        return cart.cartItems

    async def clear_cart(self, user_id):
        user = await self.prisma.user.find_first(where={'id': user_id}, include={'cart': {'include': {'cartItems': True}}})

        await self.prisma.cart.update(
            where={
                'id': user.cart[0].id
            },

            data={
                'cartItems': {
                    'set': []
                }
            }
        )

    async def delete_item(self, item_id):
        await self.prisma.item.delete(where={'id': item_id})

    # ? ORDER RELATED METHODS
    async def create_order(self, user_id, cart_items, total_amount, photo_prepayment, address):
        await self.prisma.order.create(
            data={
                "userId": user_id,
                "totalAmount": total_amount,
                "status": "in_progress",
                "orderItems": {"connect": [{"id": item.id} for item in cart_items]},
                "prepayment_photo": photo_prepayment,
                "address": address
            }
        )

        await self.clear_cart(user_id)

    async def get_orders(self, user_id: str):
        # include user also
        return await self.prisma.order.find_many(where={'userId': user_id}, include={'user': True,'orderItems': {'include': {'product': True, 'productVariant': {'include': {'discounts': False, 'sizes': True}}}}})

    async def get_active_orders(self):
        return await self.prisma.order.find_many(
            where={'status': {'in': ['in_progress', 'confirmed', 'in_delivery']}},
            include={'user': True, 'orderItems': {'include': {'product': True, 'productVariant': {'include': {'discounts': False, 'sizes': True}}}}}
        )
    
    async def update_order_status(self,order_id,status):
        await self.prisma.order.update(
            where={'id':order_id},
            data={'status':status}
        )

    async def update_order_comment(self,order_id,comment):
        await self.prisma.order.update(
            where={'id':order_id},
            data={'comment':comment}
        )

    # ? DATABASE CLENUP METHODS

    async def clear_database(self):
        await self.clear_orders()
        await self.clear_users()
        await self.clear_categories()

    async def clear_users(self):
        await self.clear_items()
        
        await self.prisma.order.delete_many()
        await self.prisma.cart.delete_many()

        await self.clear_questions()
        await self.prisma.user.delete_many()

    async def clear_categories(self):
        await self.clear_subcategories()
        await self.prisma.category.delete_many()

    async def clear_subcategories(self):
        await self.clear_products()
        await self.prisma.subcategory.delete_many()

    async def clear_products(self):
        await self.clear_products_variants()
        await self.prisma.product.delete_many()

    async def clear_products_variants(self):
        await self.prisma.size.delete_many()
        await self.prisma.discount.delete_many()
        await self.prisma.productvariant.delete_many()

    async def clear_items(self):
        await self.prisma.item.delete_many()

    async def clear_orders(self):
        await self.prisma.order.delete_many()

    async def clear_questions(self):
        await self.prisma.question.delete_many()