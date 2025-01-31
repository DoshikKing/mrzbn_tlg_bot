import asyncio
import time
from datetime import datetime
import calendar
from monthdelta import monthdelta
import configparser
import logging
from marzban import MarzbanAPI, UserCreate, ProxySettings
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

config = configparser.ConfigParser()
config.read("config.ini")
host = config["MRZBN"]["ENDPOINT"]

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

marzban_api = MarzbanAPI(base_url=host)


async def get_token():
    return await marzban_api.get_token(username=config["MRZBN"]["USER"], password=config["MRZBN"]["PASS"])


async def check_user_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    token = await get_token()
    user_id = str(update.effective_user.id)
    user_info = await marzban_api.get_user(username=user_id, token=token.access_token)
    await update.message.reply_text(user_info.status)


async def check_user_expiration_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    token = await get_token()
    user_id = str(update.effective_user.id)
    user_info = await marzban_api.get_user(username=user_id, token=token.access_token)
    await update.message.reply_text(datetime.fromtimestamp(user_info.expire))


async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # if paued:
    #     await create_user(update=update, context=context)
    #     if (create_user):
    #         await update.message.reply_text(f"User created! Sub link: {create_user.link}")
    #     else:
    #         await update.message.reply_text("Cannot create user!")    
    # else:
    #     await update.message.reply_text("Payment aborted!")
    pass 


async def create_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    token = await get_token()
    user_id = str(update.effective_user.id)
    if check_user_status is not None:
        expiration_time = calendar.timegm((datetime.now() + monthdelta(1)).timetuple()) # 28 days.. need to fix
        new_user = UserCreate(username=user_id, expire=expiration_time, proxies={"vless": ProxySettings()}, inbounds={'vless': ['VLESS TCP REALITY']})
        added_user = await marzban_api.add_user(user=new_user, token=token.access_token)


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')


if __name__ == '__main__':
    app = ApplicationBuilder().token(config["TELEGRAM"]["TOKEN"]).build()
    app.add_handler(CommandHandler("hello", hello))
    app.add_handler(CommandHandler("status", check_user_status))
    app.add_handler(CommandHandler("expire", check_user_expiration_time))
    app.add_handler(CommandHandler("create", create_user))
    app.run_polling()