from abc import ABC, abstractmethod

class Document(ABC):
    @abstractmethod
    def __init__(self, modified, retro):
        self.retro = retro
        self.modified = modified
        pass

    def modify(self, modified):
        self.modified = modified
        return modified

    def to_retro(self, retro):
        self.retro = retro
        return retro