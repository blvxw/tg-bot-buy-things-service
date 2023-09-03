def check_query(query, cur_handler: str):
    handler = query.data.split(':')[0]

    if handler == cur_handler:
        print(f'\033[92m[BOT]\033[0m {query.from_user.first_name} >>> {query.data}')
        return True
    
    return False