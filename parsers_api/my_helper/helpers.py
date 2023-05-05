import asyncio
import math

from parsers_api.currency_rate import CurrencyRate


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


def get_price_rub(price, currency):
    return math.ceil(CurrencyRate.get_rate(currency) * price)
