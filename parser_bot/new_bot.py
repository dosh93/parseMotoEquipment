import asyncio
import configparser
from typing import List
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor
from aiohttp import ClientSession

from common.logger import configure_logger

logger = configure_logger(__name__)

config = configparser.ConfigParser()
config.read("config.ini")

BOT_TOKEN = config.get("bot", "token")
ALLOWED_CHAT_IDS = [int(chat_id.strip()) for chat_id in config.get("bot", "allowed_chat_ids").split(",")]
API_HOST = config.get("api", "host")
API_PORT = config.get("api", "port")

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
markup.row("Добавить", "Обновить все цены", "Обновить цену товара")


class AddProduct(StatesGroup):
    waiting_for_links = State()


class UpdatePrice(StatesGroup):
    waiting_for_url_or_id = State()


async def on_startup(dp):
    logger.info(f"Start bot")


@dp.message_handler(commands=["start"], chat_id=ALLOWED_CHAT_IDS)
async def start(message: types.Message):
    logger.info(f"Start command {message.text} with chat_id {message.chat.id}")
    await message.reply("Выберите действие:", reply_markup=markup)
    logger.info(f"End command {message.text} with chat_id {message.chat.id}")


@dp.message_handler(lambda message: message.text == "Добавить", chat_id=ALLOWED_CHAT_IDS)
async def add_product(message: types.Message):
    logger.info(f"Start command {message.text} with chat_id {message.chat.id}")
    await message.reply("Отправьте ссылки через пробел")
    await AddProduct.waiting_for_links.set()
    logger.info(f"End command {message.text} with chat_id {message.chat.id}")


@dp.message_handler(lambda message: message.text == "Обновить все цены", chat_id=ALLOWED_CHAT_IDS)
async def update_prices(message: types.Message):
    logger.info(f"Start command {message.text} with chat_id {message.chat.id}")
    async with ClientSession() as session:
        async with session.get(f"{API_HOST}:{API_PORT}/update_prices") as resp:
            result = await resp.text()
            await message.reply(result)
    logger.info(f"End command {message.text} with chat_id {message.chat.id}")


@dp.message_handler(lambda message: message.text == "Обновить цену товара", chat_id=ALLOWED_CHAT_IDS)
async def update_price(message: types.Message):
    logger.info(f"Start command {message.text} with chat_id {message.chat.id}")
    await message.reply("Отправьте ссылку или ID товара")
    await UpdatePrice.waiting_for_url_or_id.set()
    logger.info(f"End command {message.text} with chat_id {message.chat.id}")


@dp.message_handler(lambda message: message.text, state=AddProduct.waiting_for_links,
                    content_types=types.ContentTypes.TEXT, chat_id=ALLOWED_CHAT_IDS)
async def process_links(message: types.Message, state):
    logger.info(f"Start command {message.text} with chat_id {message.chat.id}")
    links = message.text.split(" ")
    cleaned_links = [link.split("#")[0] for link in links]

    async with ClientSession() as session:
        for link in cleaned_links:
            async with session.get(f"http://{API_HOST}:{API_PORT}/add_product?url={link}") as resp:
                result = await resp.text()
                await message.reply(result)

    await state.finish()
    await message.reply("Готово!", reply_markup=markup)
    logger.info(f"End command {message.text} with chat_id {message.chat.id}")


@dp.message_handler(lambda message: message.text, state=UpdatePrice.waiting_for_url_or_id,
                    content_types=types.ContentTypes.TEXT, chat_id=ALLOWED_CHAT_IDS)
async def process_url_or_id(message: types.Message, state):
    logger.info(f"Start command {message.text} with chat_id {message.chat.id}")
    data = message.text
    if data.startswith("http://") or data.startswith("https://"):
        api_url = f"http://{API_HOST}:{API_PORT}/update_price?url={data}"
    else:
        api_url = f"http://{API_HOST}:{API_PORT}/update_price?id={data}"

    async with ClientSession() as session:
        async with session.get(api_url) as resp:
            result = await resp.text()

    await message.reply(result, reply_markup=markup)
    await state.finish()
    logger.info(f"End command {message.text} with chat_id {message.chat.id}")


if __name__ == "__main__":
    dp.middleware.setup(LoggingMiddleware())
    executor.start_polling(dp, on_startup=on_startup)
