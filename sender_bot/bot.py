import configparser
import json
import os

from quart import Quart, request
from aiogram import Bot, Dispatcher, types
from datetime import datetime

from common.logger import configure_logger

logger = configure_logger(__name__)

config = configparser.ConfigParser()
current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_dir, "config.ini")

config.read(config_path)

BOT_TOKEN = config.get("bot", "token")
CHANNEL_ID_SERVICE = config.get('bot', 'channel_id_service')
CHANNEL_ID_NEW_SIZE = config.get('bot', 'channel_id_new_size')
CHANNEL_ID_NEW_PRICE = config.get('bot', 'channel_id_new_price')
MAX_MESSAGE_SIZE = config.getint('bot', 'max_message_size')

host = config.get('flask_app', 'host', fallback='0.0.0.0')
port = config.getint('flask_app', 'port', fallback=8080)

app = Quart(__name__)

bot = Bot(token=BOT_TOKEN)


async def process_message_parsers_api(text, type_message):
    json_obj = json.loads(text)
    now = datetime.now()

    if type_message == 'new_size':
        text = f"{now.strftime('%d-%m-%Y')}\n<b>Добавились новые размеры</b>\n"
        for one in json_obj:
            current_text = "----------\n"
            current_text += f"<a href='{one['url']}'>{one['name']}</a>\n"
            for new_size in one['new_size']:
                current_text += f"{new_size['color']} {new_size['size']}\n"
            if len(current_text) + len(text) > MAX_MESSAGE_SIZE:
                await bot.send_message(CHANNEL_ID_NEW_SIZE, text, parse_mode='HTML', disable_web_page_preview=True)
                text = current_text
            else:
                text += current_text
        await bot.send_message(CHANNEL_ID_NEW_SIZE, text, parse_mode='HTML', disable_web_page_preview=True)
    elif type_message == 'new_price':
        text = f"{now.strftime('%d-%m-%Y')}\n<b>Снизились цены</b>\n"
        for one in json_obj:
            current_text = "----------\n"
            current_text += f"<a href='{one['url']}'>{one['name']}</a>\n"
            for new_price in one['new_price']:
                current_text += f"{new_price['color']}: "
                first_variant = new_price['variants'][0]
                current_text += f"{first_variant['old_price']}€ ➡️ {first_variant['new_price']}€\n"

            if len(current_text) + len(text) > MAX_MESSAGE_SIZE:
                await bot.send_message(CHANNEL_ID_NEW_PRICE, text, parse_mode='HTML', disable_web_page_preview=True)
                text = current_text
            else:
                text += current_text
        await bot.send_message(CHANNEL_ID_NEW_PRICE, text, parse_mode='HTML', disable_web_page_preview=True)
    else:
        await bot.send_message(CHANNEL_ID_SERVICE, text)


@app.route('/send_message', methods=['GET'])
async def handle():
    text = request.args.get('text', '')
    name_service = request.args.get('service_name', '')
    type_message = request.args.get('type_message', '')
    if name_service == "parsers_api":
        await process_message_parsers_api(text, type_message)
    else:
        await bot.send_message(CHANNEL_ID_SERVICE, text)
    logger.info(f'Send message {name_service}')

    return 'OK'


@app.before_serving
async def startup():
    logger.info('Starting up...')


if __name__ == '__main__':
    app.run(host=host, port=port)

