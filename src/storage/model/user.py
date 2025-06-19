from .doc import Document


class User(Document):
    def __init__(self, modified, retro, user_id: str):
        self.user_id = user_id
