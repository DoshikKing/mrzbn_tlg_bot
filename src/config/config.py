# Holds app config context
from argparse import ArgumentParser
from configparser import ConfigParser
from datetime import timedelta, timezone


class Config:
    def __init__(self):
        parser = ArgumentParser()
        parser.add_argument('--settings', dest='settings', type=str, help='Specify settings file path')
        config = ConfigParser()
        config.read(parser.parse_args().settings)

        self.db_name = config["STORAGE"]["DATABASE"]
        self.db_host = config["STORAGE"]["HOST"]
        self.db_port = config["STORAGE"]["PORT"]
        self.db_user = config["STORAGE"]["USER"]
        self.db_pass = config["STORAGE"]["PASS"]
        self.proxy_type = config["PROXY"]["TYPE"]
        self.proxy_base_url = config["PROXY"]["ENDPOINT"]
        self.proxy_admin_user = config["PROXY"]["USER"]
        self.proxy_admin_pass = config["PROXY"]["PASS"]
        self.tg_token = config["TELEGRAM"]["TOKEN"]
        self.admin_id = config["ADMIN"]["ID"]
        self.admin_chat_id = config["ADMIN"]["CHAT"]
        self.card_code = config["CARD"]["NUM"]
        self.timezone = timezone(timedelta(hours=3))

    def get_proxy_base_url(self):
        return self.proxy_base_url

    def get_proxy_admin_user(self):
        return self.proxy_admin_user

    def get_proxy_admin_pass(self):
        return self.proxy_admin_pass

    def get_tg_token(self):
        return self.tg_token

    def get_admin_id(self):
        return self.admin_id

    def get_admin_chat_id(self):
        return self.admin_chat_id

    def get_card_code(self):
        return self.card_code

    def get_timezone(self):
        return self.timezone