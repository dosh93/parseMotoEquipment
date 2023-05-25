import asyncio
import math
import os
from configparser import ConfigParser

import requests

config = ConfigParser()
config_file_path = os.path.join(os.path.dirname(__file__), '..', 'config.ini')
config.read(config_file_path)


async def retry_on_error(func, end_func, *args, max_retries=3, delay=1):
    retries = 0

    while retries <= max_retries:
        try:
            result = await func(*args)
            return result
        except Exception as e:
            print(f"Ошибка: {e}. Попытка {retries + 1} из {max_retries}.")
            retries += 1
            await end_func()
            await asyncio.sleep(delay)

    raise Exception("Превышено максимальное число попыток.")


def get_price_rub(price, rate):
    return math.ceil(rate * price)


def send_service_message(message):
    url = config.get('send_message', 'url')
    requests.get(url, params={'text': message, 'service_name': 'parsers_api'})
