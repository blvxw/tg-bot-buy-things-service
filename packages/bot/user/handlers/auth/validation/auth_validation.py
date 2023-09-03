# >>> REGEX
import re

# >>> db
from packages.services.prisma_service import PrismaService

# >>> base validation class
from packages.bot.user.handlers.auth.validation.base_validation import BaseValidation

class AuthValidation(BaseValidation):
    def __init__(self):
        self.prisma_service = PrismaService()

    def checkName(self, name):
        return BaseValidation._checkValue(name, AuthValidation._regexForName().match)

    def checkSurname(self, surname):
        return BaseValidation._checkValue(surname, AuthValidation._regexForName().match)

    async def checkEmail(self, email):
        if not BaseValidation._checkValue(email, AuthValidation._regexForEmail().match):
            return False

        if await self.prisma_service.check_user_exists_column('email', email):
            return False

        return True

    async def checkPhone(self, phone):
        if not BaseValidation._checkValue(phone, AuthValidation._regexForPhone().match):
            return False

        if await self.prisma_service.check_user_exists_column('phone', phone):
            return False

        return True

    @staticmethod
    def _regexForName():
        return re.compile(r'^[a-zA-Zа-яА-Я]{2,20}$')

    @staticmethod
    def _regexForEmail():
        return re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+[a-zA-Z0-9.-]+$')

    @staticmethod
    def _regexForPhone():
        return re.compile(r'^\+\d{1,3}\d{7,10}$')