import argparse
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

parser = argparse.ArgumentParser()
parser.add_argument('--settings', dest='settings', type=str, help='Specify settings file path')
args = parser.parse_args()

config = configparser.ConfigParser()
config.read(args.settings)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.INFO)
logger = logging.getLogger(__name__)

api = MarzbanAPI(base_url=config["MRZBN"]["ENDPOINT"])
marz_token = MarzbanTokenCache(
        client=api,
        username=config["MRZBN"]["USER"], password=config["MRZBN"]["PASS"],
        token_expire_minutes=1440
    )


# Checks if user exists and returns user info
async def check_and_get_user(user_id: str):
    try:
        return await api.get_user(username=user_id, token=await marz_token.get_token())
    except:
        logger.error("No user with id %s", user_id, exc_info=True)


# Updates user via mod_data and returns status
async def update_user_ex_time(user_id: str, mod_data:UserModify):
    try:
        return await api.modify_user(username=user_id, user=UserModify(expire=expiration_time), token=await marz_token.get_token())
    except:
        logger.error("Cant update user with id %s", user_id, exc_info=True)


# Creates new user with user_id
async def create_new_user(user_id: str):
    try:
        if check_user_status(user_id=user_id) is not None:
            expiration_time = calendar.timegm((datetime.now() + monthdelta(1)).timetuple()) # 28 days.. need to fix
            new_user = UserCreate(username=user_id, expire=expiration_time, proxies={"vless": ProxySettings()}, inbounds={'vless': ['VLESS TCP REALITY']})
            return await api.add_user(user=new_user, token=await marz_token.get_token())
    except:
        logger.error("No user with id %s", user_id, exc_info=True)


async def remove_ex_user(user_id: str):
    await api.remove_user(username=user_id, token=await marz_token.get_token())


##########################################################################################################################
#                                                    Bot commands                                                        #
##########################################################################################################################
async def check_user_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_info = await check_and_get_user(user_id=str(context._user_id))
    await update.message.reply_text(user_info.status)


async def check_user_expiration_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_info = await check_and_get_user(user_id=str(context._user_id))
    await update.message.reply_text(str(datetime.fromtimestamp(int(user_info.expire))))


async def update_user_expiration_time(context: ContextTypes.DEFAULT_TYPE) -> None:
    expiration_time = calendar.timegm((datetime.now() + monthdelta(1)).timetuple())
    return await update_user_ex_time(username=str(context._user_id), user=UserModify(expire=expiration_time))


async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # impl pay process
    some


# Admin only
async def create_user(context: ContextTypes.DEFAULT_TYPE) -> None:
    user = await create_new_user(user_id=str(context._user_id))
    if user != None:
        await update.message.reply_text("New account created!")


async def remove_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await remove_ex_user(user_id=str(context._user_id))
    await update.message.reply_text("Removed acc!")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f' \
        Hello {update.effective_user.first_name}! \
        What would you like to do? \
        1. Pay: /pay \
        2. Check sub time: /expire \
        3. Check sub status: /status \
    ')


if __name__ == '__main__':
    app = ApplicationBuilder().token(config["TELEGRAM"]["TOKEN"]).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("pay", pay))
    app.add_handler(CommandHandler("status", check_user_status))
    app.add_handler(CommandHandler("expire", check_user_expiration_time))
    app.add_handler(CommandHandler("remove", remove_user))
    app.run_polling()