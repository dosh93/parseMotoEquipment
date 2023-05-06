import requests
import json
from datetime import datetime, timedelta

from common.logger import configure_logger

logger = configure_logger(__name__)


class CurrencyRate:
    _url = "https://www.cbr-xml-daily.ru/daily_json.js"
    _last_update = None
    _data = None

    @classmethod
    def _fetch_data(cls):
        response = requests.get(cls._url)
        logger.info("Fetching data")
        logger.debug(response.text)
        if response.status_code == 200:
            cls._data = json.loads(response.text)
            cls._last_update = datetime.now()
        else:
            logger.error("Не удалось получить данные о курсе валют")

    @classmethod
    def get_rate(cls, valute_name):
        if cls._data is None or cls._last_update is None or datetime.now() - cls._last_update > timedelta(days=1):
            cls._fetch_data()

        if valute_name in cls._data["Valute"]:
            return float(cls._data["Valute"][valute_name]["Value"]) + 2
        else:
            logger.error(f"Валюта '{valute_name}' не найдена")
