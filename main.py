import argparse
import schedule
import asyncio
import time
from datetime import datetime
import calendar
from monthdelta import monthdelta
import configparser
import logging
import random
from marzban import MarzbanAPI, UserCreate, ProxySettings, UserModify, MarzbanTokenCache
from telegram import Update, MenuButton
from telegram.ext import Application, ApplicationBuilder, CommandHandler, ConversationHandler, MessageHandler, ContextTypes, filters

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

admin = {"id": config["ADMIN"]["ID"], "chat": config["ADMIN"]["CHAT"]}
card_number = "3123213213213123"

NEW, PROCESSING, DONE = range(3)

p_user_tasks = []


##########################################################################################################################
#                                                    MRZB commands                                                       #
##########################################################################################################################
# Checks if user exists and returns user info
async def check_and_get_user(user_id: str):
    try:
        return await api.get_user(username=user_id, token=await marz_token.get_token())
    except:
        logger.error("No user with id %s", user_id, exc_info=True)


# Updates user via mod_data and returns status
async def update_user_ex_time(user_id: str, mod_data:UserModify):
    try:
        if check_and_get_user(user_id=user_id) is not None:
            return await api.modify_user(username=user_id, user=mod_data, token=await marz_token.get_token())
    except:
        logger.error("Cant update user with id %s", user_id, exc_info=True)


# Creates new user with user_id
async def create_new_user(user_id: str):
    try:
        if check_and_get_user(user_id=user_id) is None:
            expiration_time = calendar.timegm((datetime.now() + monthdelta(1)).timetuple()) # 28 days.. need to fix
            new_user = UserCreate(username=user_id, expire=expiration_time, proxies={"vless": ProxySettings()}, inbounds={'vless': ['VLESS TCP REALITY']})
            return await api.add_user(user=new_user, token=await marz_token.get_token())
    except:
        logger.error("No user with id %s", user_id, exc_info=True)

# Deletes user by user_id
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


async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(context._user_id)
    chat_id = str(context._chat_id)
    code = str(random.randint(0, 999999)).zfill(6) # gen random code
    p_user_tasks.append({"id": user_id, "chat": chat_id, "code": code, "status": NEW})
    await update.message.reply_text(f' \
        Payment process: \
        Send $ to card {card_number} with code in description {code} \
        Then wait for admin approval! \
    ')
    await manage_payment(app=context)


async def remove_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await remove_ex_user(user_id=str(context._user_id))
    await update.message.reply_text("Removed acc!")


async def get_chat_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'id: {str(context._user_id)} chat_id: {str(context._chat_id)}')


async def get_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Stats: {p_user_tasks}')


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f' \
        Hello {update.effective_user.first_name}! \
        What would you like to do? \
        1. Pay: /pay \
        2. Check sub time: /expire \
        3. Check sub status: /status \
    ')


async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("approve() >> I GOT HERE!")
    if str(context._user_id) == admin["id"]:
        for user_task in p_user_tasks:
            logger.info(f"approve() >> I GOT HERE! {user_task["status"]}")
            if user_task["code"] == update.message.text and user_task["status"] == PROCESSING:
                if check_and_get_user(user_id=user_task["id"]) is None:
                    await create_new_user(user_id=user_task["id"])
                else:
                    expiration_time = calendar.timegm((datetime.now() + monthdelta(1)).timetuple()) # 28 days bag
                    await update_user_ex_time(user_id=user_task["id"], mod_data=UserModify(expire=expiration_time))
                user_task["status"] = DONE
                await context.bot.send_message(user_task["chat"], 'Admin approved your transaction! Enjoy!')
            else:
                await context.bot.send_message(admin["chat"], 'Wrong code!')


##########################################################################################################################
#                                                    Internal commands                                                   #
##########################################################################################################################
async def manage_payment(app: ContextTypes.DEFAULT_TYPE):
    for user_task in p_user_tasks:
        if (user_task["status"] == NEW):
            # not updating
            user_task["status"] = PROCESSING
            await app.bot.send_message(admin["chat"], f'User {user_task["id"]} payed with code {user_task["code"]}. Type code to permit..')


if __name__ == '__main__':
    app = ApplicationBuilder().token(config["TELEGRAM"]["TOKEN"]).build()
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("pay", pay))
    app.add_handler(CommandHandler("status", check_user_status))
    app.add_handler(CommandHandler("expire", check_user_expiration_time))
    app.add_handler(CommandHandler("remove", remove_user))
    app.add_handler(CommandHandler("inf", get_chat_info))
    app.add_handler(CommandHandler("gts", get_stats))
    app.add_handler(MessageHandler(filters.TEXT, approve))
    app.run_polling()