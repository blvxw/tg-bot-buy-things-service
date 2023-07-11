import dotenv


def get_env_variable(key):
    return dotenv.get_key('.env', key)
