from logging import Logger

from marzban import MarzbanAPI, UserCreate, ProxySettings, UserModify, MarzbanTokenCache, UserResponse, UsersResponse

from .proxy import Proxy


class MrzbnProxy(Proxy):
    def __init__(
            self,
            base_url: str,
            username: str,
            password: str,
            logger: Logger
    ):
        self.client = MarzbanAPI(base_url=base_url)
        self.token = MarzbanTokenCache(client=self.client,
                                       username=username, password=password,
                                       token_expire_minutes=1440)
        self.logger = logger

    async def get_users(self) -> UsersResponse | None:
        try:
            return await self.client.get_users(token=await self.token.get_token())
        except:
            self.logger.error("No users found!", exc_info=True)
            return None

    # Checks if user exists and returns user info
    async def check_and_get_user(self, user_id: str) -> UserResponse | None:
        try:
            return await self.client.get_user(username=user_id, token=await self.token.get_token())
        except:
            self.logger.error("No user with id %s", user_id, exc_info=True)
            return None

    # Updates user via mod_data and returns status
    async def update_user_ex_time(self, user_id: str, ex_time: int) -> UserResponse | None:
        try:
            user = await self.check_and_get_user(user_id=user_id)
            if user is not None:
                return await self.client.modify_user(username=user_id, user=UserModify(expire=ex_time),
                                                     token=await self.token.get_token())
            return None
        except:
            self.logger.error('Cant update user with id %s', user_id, exc_info=True)
            return None

    # Creates new user with user_id
    async def create_new_user(self, user_id: str, ex_time: int) -> UserResponse | None:
        try:
            if await self.check_and_get_user(user_id=user_id) is None:
                new_user = UserCreate(username=user_id, expire=ex_time, proxies={"vless": ProxySettings()},
                                      inbounds={'vless': ['VLESS TCP REALITY']})
                return await self.client.add_user(user=new_user, token=await self.token.get_token())
            return None
        except:
            self.logger.error('No user with id %s', user_id, exc_info=True)
            return None

    # Deletes user by user_id
    async def remove_ex_user(self, user_id: str) -> UserResponse | None:
        await self.client.remove_user(username=user_id, token=await self.token.get_token())
