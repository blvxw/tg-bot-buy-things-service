import re
from packages.services.prisma_service import PrismaService
from packages.bot.common.handlers.auth.validation.base_validation import BaseValidation
from packages.utils.contsants import *

class AuthValidation(BaseValidation):
    def __init__(self):
        self.prisma_service = PrismaService()
    
    def checkName(self, name):
        return BaseValidation._checkValue(name, AuthValidation._regexForName().match)

    def checkSurname(self, surname):
        return BaseValidation._checkValue(surname, AuthValidation._regexForName().match)
    
    async def checkEmail(self, email):
        if not BaseValidation._checkValue(email, AuthValidation._regexForEmail().match):
            return VALUE_IS_NOT_VALID
        
        if await self.prisma_service.checkUserExistsColumn('email', email) == True:
            return VALUE_ALREDY_EXIST
        
        return True

    async def checkPhone(self, phone):
        if not BaseValidation._checkValue(phone, AuthValidation._regexForPhone().match):
            return VALUE_IS_NOT_VALID
        # if phone exists in db return False
        if await self.prisma_service.checkUserExistsColumn('phone', phone) == True:
            return VALUE_ALREDY_EXIST
        
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