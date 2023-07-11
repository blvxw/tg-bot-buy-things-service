class User():
    def __init__(self):
        self.telegram_id = None
        self.name = None
        self.surname = None
        self.phone = None
        self.email = None
        self.language = None
        self.role = None
        
    def __init__(self, telegram_id, name, surname, phone, email, language,role):
        self.telegram_id = telegram_id
        self.name = name
        self.surname = surname
        self.phone = phone
        self.email = email
        self.language = language
        self.role = role

    def allFieldsFilled(self):
        return self.telegram_id and self.name and self.surname and self.phone and self.email and self.language
    