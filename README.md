# Telegram bot for Marzban VPN managment!

# INFO
Lets you manage your Marzban instance using Telegram bot

Functionality:
Regular user:
1. Pay option for regular user (or you can rename it to 'grant access' or smth)
2. Get status of the account
3. Get expiration time of the account
4. Get subscription link
5. Get help info
Admin:
1. Admin can grant user a vpn access (creating account or reviving expired one)
2. More soon!

Built with:
- python-telegram-bot
- marzban-api
- more in [requirements file](requirements.txt)

# Requirements and prerequisites 
Required:
1. Python 3.13.1 or higher
2. Libs from [requirements file](requirements.txt)
Before launch
1. Needs [settings file](settings.ini). All params are self explanatory. More about [Telegarm API](https://core.telegram.org/bots/api) and [Marzban API](https://gozargah.github.io/marzban/en/)

# Install and run!
Options:
1. Install dependencies via [requirements file](requirements.txt) like 
```shell
pip install -r requirements.txt
``` 
and launch [main.py](main.py) like
```shell
python main.py --settings YOUR_SETTINGS_FILE
``` 
2. Build docker image from [Dockerfile](Dockerfile) and run like
```shell
docker build -t boatapp:v1 .
docker run -p 8080:80 boatapp:v1
``` 
