import configparser
import re
import aiohttp
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode
from aiogram import executor
from parser_bot.logger import configure_logger

logger = configure_logger(__name__)

config = configparser.ConfigParser()
config.read("config.ini")

BOT_TOKEN = config["bot"]["token"]
ALLOWED_CHAT_IDS = list(map(int, config["bot"]["allowed_chat_ids"].split(',')))

API_HOST = config["api"]["host"]
API_PORT = config["api"]["port"]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())


def is_url(string: str) -> bool:
    url_regex = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    return re.match(url_regex, string) is not None


def clean_url(url: str) -> str:
    return url.split("#")[0]


async def api_request(path: str, params=None) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://{API_HOST}:{API_PORT}/{path}", params=params) as resp:
            return await resp.text()


async def on_start(message: types.Message):
    if message.chat.id not in ALLOWED_CHAT_IDS:
        return

    text = md.text(
        md.text("Привет! Я ваш помощник."),
        sep="\n",
    )

    await message.reply(text, parse_mode=ParseMode.MARKDOWN)


async def on_add_product(message: types.Message, data: str):
    if message.chat.id not in ALLOWED_CHAT_IDS:
        return
    cleaned_url = clean_url(data)
    response = await api_request("add_product", {"url": cleaned_url})
    await message.reply(response)


async def on_update_all_price(message: types.Message):
    if message.chat.id not in ALLOWED_CHAT_IDS:
        return

    response = await api_request("update_prices")
    await message.reply(response)


async def on_update_one_price(message: types.Message, data: str):
    if message.chat.id not in ALLOWED_CHAT_IDS:
        return

    if is_url(data):
        cleaned_url = clean_url(data)
        params = {"url": cleaned_url}
    else:
        params = {"id": data}

    response = await api_request("update_price", params)
    await message.reply(response)


@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    logger.info(f"Start command {message.text} with chat_id {message.chat.id}")
    await on_start(message)
    logger.info(f"End command {message.text} with chat_id {message.chat.id}")


@dp.message_handler(lambda message: message.text.startswith("/add "))
async def add_product_handler(message: types.Message):
    logger.info(f"Start command {message.text} with chat_id {message.chat.id}")
    data = message.text[4:].strip()
    await on_add_product(message, data)
    logger.info(f"End command {message.text} with chat_id {message.chat.id}")


@dp.message_handler(commands=["update_all"])
async def update_all_price_handler(message: types.Message):
    logger.info(f"Start command {message.text} with chat_id {message.chat.id}")
    await on_update_all_price(message)
    logger.info(f"End command {message.text} with chat_id {message.chat.id}")


@dp.message_handler(lambda message: message.text.startswith("/update_one "))
async def update_one_price_handler(message: types.Message):
    logger.info(f"Start command {message.text} with chat_id {message.chat.id}")
    data = message.text[12:].strip()
    await on_update_one_price(message, data)
    logger.info(f"End command {message.text} with chat_id {message.chat.id}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
