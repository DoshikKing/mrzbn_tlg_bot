# Holds app config context
from argparse import ArgumentParser
from configparser import ConfigParser


class Config:
    def __init__(self, ):
        parser = ArgumentParser()
        parser.add_argument('--settings', dest='settings', type=str, help='Specify settings file path')
        config = ConfigParser()
        config.read(parser.parse_args().settings)
        self.proxy_base_url = config["MRZBN"]["ENDPOINT"]
        self.proxy_admin_user = config["MRZBN"]["USER"]
        self.proxy_admin_pass = config["MRZBN"]["PASS"]
        self.tg_token = config["TELEGRAM"]["TOKEN"]
        self.admin_id = config["ADMIN"]["ID"]
        self.admin_chat_id = config["ADMIN"]["CHAT"]
        self.card_code = config["CARD"]["NUM"]

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
