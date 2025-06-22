from abc import ABC, abstractmethod
from datetime import datetime

class Document(ABC):
    @abstractmethod
    def __init__(self, doc_id, retro):
        self.doc_id = doc_id
        self.modified = None
        self.retro = retro

    def modify(self, app_timezone):
        self.modified = datetime.now(app_timezone)
        return self.modified

    def to_retro(self, retro):
        self.retro = retro
        return self.retro