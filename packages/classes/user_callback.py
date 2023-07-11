from enum import Enum


class UserCallback(Enum):
    #? menu
    USER_MAIN_MENU = 'user_menu'
    USER_SETTINGS_MENU = 'user_settings_menu'
    
    #? actions
    USER_CATALOGS = 'user_catalogs'
    USER_PRODUCTS_IN_CATALOG = 'user_products_in_catalog'
    USER_CART = 'user_cart'
    USER_ORDERS = 'user_orders'
    CHOOSE_SHOW_ADULT_CONTENT = 'choose_show_adult_content'
    CHANGE_LANGUAGE = 'change_language'

    #? products
    USER_SHOW_PAGE_OF_PRODUCTS = 'user_show_page_of_products'