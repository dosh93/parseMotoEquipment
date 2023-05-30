import asyncio
import configparser
import os
from typing import List
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor
from aiogram.utils.callback_data import CallbackData
from aiohttp import ClientSession

from common.logger import configure_logger

logger = configure_logger(__name__)

config = configparser.ConfigParser()
current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_dir, "config.ini")

config.read(config_path)

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
category_callback = CallbackData("category", "id", "name")
current_category = {}


class AddProduct(StatesGroup):
    waiting_for_links = State()


class UpdatePrice(StatesGroup):
    waiting_for_url_or_id = State()


async def fetch(url):
    async with ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()


async def get_button_category():
    keyboard = InlineKeyboardMarkup()
    categories = await fetch(f"http://{API_HOST}:{API_PORT}/get_categories")
    for category in categories:
        keyboard.add(InlineKeyboardButton(category['name'], callback_data=category_callback.new(id=category['id'],
                                                                                                name=category['name'])))
    return keyboard


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
    await message.reply("Выберете категорию:", reply_markup=await get_button_category())
    logger.info(f"End command {message.text} with chat_id {message.chat.id}")


@dp.callback_query_handler(category_callback.filter())
async def category_callback_handler(query: types.CallbackQuery, callback_data: dict):
    await query.answer()
    logger.info(f"Start command {callback_data} with chat_id {query.message.chat.id}")
    category_id = callback_data['id']
    category_name = callback_data['name']
    current_category[query.message.chat.id] = category_id
    await AddProduct.waiting_for_links.set()
    await bot.send_message(query.from_user.id, "Отправьте ссылки через пробел")
    logger.info(f"End command {callback_data} with chat_id {query.message.chat.id}")


@dp.message_handler(lambda message: message.text == "Обновить все цены", chat_id=ALLOWED_CHAT_IDS)
async def update_prices(message: types.Message):
    logger.info(f"Start command {message.text} with chat_id {message.chat.id}")
    async with ClientSession() as session:
        async with session.get(f"http://{API_HOST}:{API_PORT}/update_prices") as resp:
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
            async with session.get(
                    f"http://{API_HOST}:{API_PORT}/add_product?url={link}&category_id={current_category[message.chat.id]}") as resp:
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
