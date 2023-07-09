def isQueryDataValid(query, curHandler):
    handler = query.data.split(':')[0]
    print(handler, curHandler)
    return handler == curHandler