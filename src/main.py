import logging
import random
from datetime import datetime
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

from util.ex_time_calc import get_exp_for_new_user, get_exp_time_based_on_prev
from proxy.mrzbn_proxy import MrzbnProxy
from config.config import Config

# config
config = Config()

# logger
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.INFO)
logger = logging.getLogger(__name__)

# envs
base_url = config.get_proxy_base_url()
admin = {"id": config.get_admin_id(), "chat": config.get_admin_chat_id()}
card_number = config.get_card_code()

proxy = MrzbnProxy(base_url=base_url, username=config.get_proxy_admin_user(), password=config.get_proxy_admin_pass(), logger=logger)

NEW, PROCESSING = range(2)

p_user_tasks = []

parse_mode = ParseMode.MARKDOWN_V2

##########################################################################################################################
#                                                    Bot commands                                                        #
##########################################################################################################################
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    kb = [[
        KeyboardButton('/pay'),
        KeyboardButton('/status'),
        KeyboardButton('/expire'),
        KeyboardButton('/link'),
        KeyboardButton('/help')
    ]]
    kb_markup = ReplyKeyboardMarkup(kb, resize_keyboard=True)
    await update.message.reply_text(
        f'Hello {update.effective_user.first_name}!\n\
        What would you like to do?\n\
        1. Pay: /pay\n\
        2. Check sub time: /expire\n\
        3. Check sub status: /status\n\
        4. Get sub link: /link\n\
        5. Get help: /help\n',
        reply_markup=kb_markup
    )


async def check_user_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_info = await proxy.check_and_get_user(user_id=str(context._user_id))
    if user_info is not None:
        await update.message.reply_text(user_info.status)
    else:
        await update.message.reply_text('Can\'t find your account! Maybe it\'s expired?')


async def check_user_expiration_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_info = await proxy.check_and_get_user(user_id=str(context._user_id))
    if user_info is not None:
        await update.message.reply_text(str(datetime.fromtimestamp(int(user_info.expire))))
    else:
        await update.message.reply_text('Can\'t find your account! Maybe you didn\'t have one yet?')


async def get_sub_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_info = await proxy.check_and_get_user(user_id=str(context._user_id))
    if user_info is not None:
        await update.message.reply_text(f'Your link is `{base_url + user_info.subscription_url}`', parse_mode=parse_mode)
    else:
        await update.message.reply_text('Can\'t find your account! Maybe it\'s expired?')


async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(context._user_id)
    chat_id = str(context._chat_id)
    code = str(random.randint(0, 999999)).zfill(6)  # gen random code
    p_user_tasks.append({"id": user_id, "chat": chat_id, "code": code, "status": NEW})
    await update.message.reply_text(
        f'Payment process: \n Send $ to card `{card_number}` with code `{code}` in description \n Then wait for admin approval\\!',
        parse_mode=parse_mode)
    await manage_payment(app=context)


async def helpf(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f'How to use MarzbanVPN?\n\
        1. First go to client donwload page: https://github.com/hiddify/hiddify-app/releases\n\
        2. Download version for your OS\n\
        3. Install client\n\
        4. Copy link which you get after payment (If you forget it than check it with /link !)\n\
        5. In main menu of the client press \'+\' icon and choose \'Add from clip board\'\n\
        6. After that press big button and you good to go!'
    )


async def remove_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await proxy.remove_ex_user(user_id=str(context._user_id))
    await update.message.reply_text("Removed acc!")


async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if str(context._user_id) == admin["id"]:
        for user_task in p_user_tasks:
            if user_task["code"] == str(update.message.text) and user_task["status"] == PROCESSING:
                user_id = user_task["id"]
                user = await proxy.check_and_get_user(user_id=user_id)
                if user is None:
                    user = await proxy.create_new_user(user_id=user_id, ex_time=get_exp_for_new_user(1))
                else:
                    await proxy.update_user_ex_time(user_id=user_id, ex_time=get_exp_time_based_on_prev(1, user.expire))
                await context.bot.send_message(user_task["chat"],
                                               f'Admin approved your transaction\\! Here\'s your connection link `{base_url + user.subscription_url}`\nEnjoy\\!',
                                               parse_mode=parse_mode)
                p_user_tasks.remove(user_task)
            else:
                await context.bot.send_message(admin["chat"], 'Wrong code!')


##########################################################################################################################
#                                                    Internal commands                                                   #
##########################################################################################################################
async def manage_payment(app: ContextTypes.DEFAULT_TYPE):
    for user_task in p_user_tasks:
        if (user_task["status"] == NEW):
            user_task["status"] = PROCESSING
            await app.bot.send_message(admin["chat"],
                                       f'User {user_task["id"]} payed with code `{user_task["code"]}`\\. Type code to permit\\.\\.',
                                       parse_mode=parse_mode)


if __name__ == '__main__':
    app = ApplicationBuilder().token(config.get_tg_token()).build()
    app.add_handler(CommandHandler("start", info))
    app.add_handler(CommandHandler("pay", pay))
    app.add_handler(CommandHandler("status", check_user_status))
    app.add_handler(CommandHandler("expire", check_user_expiration_time))
    app.add_handler(CommandHandler("remove", remove_user))
    app.add_handler(CommandHandler("link", get_sub_link))
    app.add_handler(CommandHandler("help", helpf))
    app.add_handler(MessageHandler(filters.TEXT, approve))
    app.run_polling()
