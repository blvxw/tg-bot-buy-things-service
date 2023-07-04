from packages.services.prisma_service import PrismaService
import asyncio

async def clear_database():
    prisma_service = PrismaService()

    await prisma_service.prisma.cartitem.delete_many()
    await prisma_service.prisma.cart.delete_many()
    await prisma_service.prisma.discount.delete_many()
    await prisma_service.prisma.size.delete_many()
    await prisma_service.prisma.productvariant.delete_many()
    await prisma_service.prisma.product.delete_many()
    await prisma_service.prisma.category.delete_many()
    await prisma_service.prisma.user.delete_many()

async def clear_users():
    prisma_service = PrismaService()

    await clear_cart_items()
    await prisma_service.prisma.cart.delete_many()
    await prisma_service.prisma.user.delete_many()
    
async def clear_categories():
    prisma_service = PrismaService()

    await clear_products()
    await prisma_service.prisma.category.delete_many()
    
async def clear_products():
    prisma_service = PrismaService()
    
    await clear_products_variants()
    await prisma_service.prisma.product.delete_many()

async def clear_products_variants():
    prisma_service = PrismaService()
    
    await prisma_service.prisma.size.delete_many()
    await prisma_service.prisma.discount.delete_many()
    await prisma_service.prisma.productvariant.delete_many()
    
async def clear_cart_items():
    prisma_service = PrismaService()

    await prisma_service.prisma.cartitem.delete_many()

