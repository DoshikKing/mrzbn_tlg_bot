from abc import ABC, abstractmethod

class Proxy(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    async def get_users(self):
        pass


    @abstractmethod
    async def check_and_get_user(self, user_id: str):
        pass


    @abstractmethod
    async def update_user_ex_time(self, user_id: str, ex_time:int):
        pass


    @abstractmethod
    async def create_new_user(self, user_id: str, ex_time: int):
        pass


    @abstractmethod
    async def remove_ex_user(self, user_id: str):
        pass

