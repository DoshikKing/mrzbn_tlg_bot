import asyncio
import time
from datetime import datetime
import calendar
from monthdelta import monthdelta
import configparser
import logging
from marzban import MarzbanAPI, UserCreate, ProxySettings, UserModify
from telegram import Update, MenuButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from payment import Payment

config = configparser.ConfigParser()
config.read("settings.ini")
host = config["MRZBN"]["ENDPOINT"]

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)

marzban_api = MarzbanAPI(base_url=host)
payment_api = "some"


async def get_token():
    return await marzban_api.get_token(username=config["MRZBN"]["USER"], password=config["MRZBN"]["PASS"])


async def check_user_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    token = await get_token()
    user_id = str(context.user_data)
    user_info = await marzban_api.get_user(username=user_id, token=token.access_token)
    await update.message.reply_text(user_info.status)


async def check_user_expiration_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    token = await get_token()
    user_id = str(context._user_id)
    user_info = await marzban_api.get_user(username=user_id, token=token.access_token)
    await update.message.reply_text(str(datetime.fromtimestamp(int(user_info.expire))))


async def update_user_expiration_time(context: ContextTypes.DEFAULT_TYPE) -> None:
    token = await get_token()
    user_id = str(context._user_id)
    expiration_time = calendar.timegm((datetime.now() + monthdelta(1)).timetuple())
    modified_user = await marzban_api.modify_user(username=user_id, user=UserModify(expire=expiration_time), token=token.access_token)
    
    return modified_user


#Need to add payment status save into context or file in case create/ update failure
async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pm = Payment()
    status = pm.process()
    if status:
        user
        exists = check_user_status(update=update, context=context)
        user = await update_user_expiration_time(context=context) if exists else await create_user(context=context)
        if user is not None:
            await update.message.reply_text(f"Got payment status! Your sub link is {user.subscription_url}. Added to your beloved app to start!")
        else:
            await update.message.reply_text("Can't create  payment status! Try again!")   
    else:
        await update.message.reply_text("Can't get payment status! Try again!")


async def create_user(context: ContextTypes.DEFAULT_TYPE) -> None:
    token = await get_token()
    user_id = str(context._user_id)
    if check_user_status is not None:
        expiration_time = calendar.timegm((datetime.now() + monthdelta(1)).timetuple()) # 28 days.. need to fix
        new_user = UserCreate(username=user_id, expire=expiration_time, proxies={"vless": ProxySettings()}, inbounds={'vless': ['VLESS TCP REALITY']})
        added_user = await marzban_api.add_user(user=new_user, token=token.access_token)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}! \
        What would you like to do? \
        1. Pay: /pay \
        2. Check sub time: /expire \
        3. Check sub status: /status \
    ')


if __name__ == '__main__':
    app = ApplicationBuilder().token(config["TELEGRAM"]["TOKEN"]).build()
    app.add_handler(CommandHandler("hello", start))
    app.add_handler(CommandHandler("pay", pay))
    app.add_handler(CommandHandler("status", check_user_status))
    app.add_handler(CommandHandler("expire", check_user_expiration_time))
    app.run_polling()