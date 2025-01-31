import asyncio
import configparser
from marzban import MarzbanAPI
config = configparser.ConfigParser()
config.read("config.ini")

host = config["MRZBN"]["ENDPOINT"]
user_id = "Lesha"
async def run():
    api = MarzbanAPI(base_url=host)
    token = await api.get_token(username=config["MRZBN"]["USER"], password=config["MRZBN"]["PASS"])
    user_info = await api.get_user(username=user_id, token=token.access_token)
    print(user_info.status)

if __name__ == '__main__':
    asyncio.run(run())