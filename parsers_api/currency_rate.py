import requests
import json
from datetime import datetime, timedelta

from common.logger import configure_logger
from parsers_api.db_conn.my_sql_connector import MySQLConnector

logger = configure_logger(__name__)


class CurrencyRate:
    _url = "https://www.cbr-xml-daily.ru/daily_json.js"
    _last_update = None
    _data = None
    _db = MySQLConnector()

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
    def get_rate_api(cls, valute_name):
        if cls._data is None or cls._last_update is None or datetime.now() - cls._last_update > timedelta(days=1):
            cls._fetch_data()

        if valute_name in cls._data["Valute"]:
            current_rate = float(cls._data["Valute"][valute_name]["Value"]) + 2
            logger.info(f"Current rate = {current_rate}")
            return current_rate
        else:
            logger.error(f"Валюта '{valute_name}' не найдена")

    @classmethod
    def get_rate_db(cls):
        rate = cls._db.get_currency_rate()
        if rate is None:
            rate = cls.get_rate_api("EUR")
        return rate
