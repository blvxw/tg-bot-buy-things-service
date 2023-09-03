from enum import Enum


class CallbackValues(Enum):
# > USER CALLBACKS
    USER_MAIN_MENU = 'user_main_menu'
    USER_SETTINGS_MENU = 'user_settings_menu'
    USER_CART_MENU = 'user_cart_menu'
    USER_CATEGORIES_MENU = 'user_categories_menu'
    USER_SUBCATEGORIES_MENU = 'user_subcategories_menu'
    USER_PRODUCTS_PAGE_MENU = 'user_products_page_menu'
    USER_PRODUCT_HANDLER = 'user_product_handler'
    USER_CHANGE_VALUE_ADULT_CONTENT = 'user_change_value_adult_content'
    USER_CHANGE_VALUE_ADULT_CONTENT_HANDLER = 'user_change_value_adult_content_handler'
    USER_CHANGE_LANGUAGE_MENU = 'user_change_language_menu'
    USER_ORDERS = 'user_orders'
    USER_HELP = 'user_help'
    SEND_QUESTION = 'user_submit_question'
    USER_ABOUT_US = 'user_about_us'
    

# > ADMIN CALLBACKS
    ADMIN_MAIN_MENU_HANDLER = 'admin_main_menu_handler'
    SHOW_ADMIN_MAIN_MENU = 'show_admin_main_menu'

    ADMIN_CATEGORIES = 'admin_categories'
    ADMIN_CATEGORY_MENU = 'admin_category_menu'
    ADMIN_SUBCATEGORY_MENU = 'admin_subcategory_menu'

    ADMIN_CHECK_QUESTIONS = 'admin_check_questions'
    ADMIN_SEND_ANSWER = "admin_send_answer"


    #* CATEGORY
    ADD_CATEGORY = 'add_category'
    DELETE_CATEGORY = 'delete_category'
    EDIT_CATEGORY = 'edit_category'

    #* SUBCATEGORY
    ADD_SUBCATEGORY = 'add_subcategory'

    #* PRODUCT
    ADD_PRODUCT = 'add_product'
    ADMIN_DELETE_PRODUCT = 'admin_delete_product'
    EDIT_PRODUCT = 'edit_product'

    #* ORDER MENU
    ADMIN_ORDERS_MENU_HANDLER = 'admin_orders_menu_handler'
    SHOW_ADMIN_ORDERS_MENU = 'show_admin_orders_menu'

    CHANGE_ORDER_STATUS = 'change_order_status'
    SET_ORDER_STATUS = 'set_order_status'
    #? ORDER STATUS
    IN_PROGRESS = 'in_process'
    CONFIRMED = 'confirmed'
    IN_DELIVERY = 'in_delivery'
    DELIVERED = 'delivered'
    CANCELED = 'canceled'

    CHANGE_ORDER_COMMENT = 'change_order_comment'

    PREVIOUS_ORDER = 'previous_order'
    NEXT_ORDER = 'next_order'

    #* QUESTIONS
    SHOW_ADMIN_QUESTIONS = 'show_admin_questions'
    ADMIN_SUBMIT_QUESTION = 'admin_submit_question'