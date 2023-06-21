import dotenv

def getEnvVar(key):
    return dotenv.get_key('.env', key)