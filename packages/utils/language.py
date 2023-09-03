import json

languages = ['en', 'ru', 'pl', 'ua']

def load_text(language, key):
    with open('resources/languages/languages.json', encoding='utf-8') as f:
        data = json.load(f)
        return data[language][key]

