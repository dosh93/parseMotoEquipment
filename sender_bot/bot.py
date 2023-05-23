import configparser
import os

from quart import Quart, request
from aiogram import Bot, Dispatcher, types

from common.logger import configure_logger

logger = configure_logger(__name__)

config = configparser.ConfigParser()
current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_dir, "config.ini")

config.read(config_path)

BOT_TOKEN = config.get("bot", "token")
CHANNEL_ID = config.get('bot', 'channel_id')

host = config.get('flask_app', 'host', fallback='0.0.0.0')
port = config.getint('flask_app', 'port', fallback=8080)

app = Quart(__name__)

bot = Bot(token=BOT_TOKEN)


@app.route('/send_message', methods=['GET'])
async def handle():
    text = request.args.get('text', '')
    name_service = request.args.get('service_name', '')
    await bot.send_message(CHANNEL_ID, text)
    logger.info(f'Send message {name_service}')

    return 'OK'


@app.before_serving
async def startup():
    logger.info('Starting up...')


if __name__ == '__main__':
    app.run(host=host, port=port)

