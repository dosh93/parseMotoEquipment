import asyncio
import datetime
import os
import mysql.connector
from configparser import ConfigParser
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode
from aiogram.utils.markdown import text

from common.logger import configure_logger

logger = configure_logger(__name__)

config = ConfigParser()
current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_dir, "config.ini")

config.read(config_path)

API_TOKEN = config.get('bot', 'token')
USER_CHAT_ID = int(config.get('bot', 'user_chat_id'))
NOTIFICATION_TIME = config.get('bot', 'notification_time')

DB_HOST = config.get('database', 'host')
DB_USER = config.get('database', 'user')
DB_PASSWORD = config.get('database', 'password')
DB_NAME = config.get('database', 'db_name')

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())


async def on_startup(dp):
    logger.info("Bot started")
    loop = asyncio.get_event_loop()
    loop.create_task(daily_notification())


async def on_shutdown(dp):
    await bot.close()
    logger.info("Bot stopped")


async def daily_notification():
    while True:
        now = datetime.datetime.now()
        target_time = datetime.datetime.strptime(NOTIFICATION_TIME, '%H:%M').time()
        if now.time() >= target_time:
            message = text("Какой сегодня курс евро к рублю?")
            await bot.send_message(chat_id=USER_CHAT_ID, text=message, parse_mode=ParseMode.MARKDOWN)
            logger.info(f"Sent message with chat_id = {USER_CHAT_ID}")
            logger.info(f"Sleep 86400 seconds")
            await asyncio.sleep(86400)
        else:
            logger.info(f"Sleep 60 seconds")
            await asyncio.sleep(60)


async def on_message(message: types.Message):
    if message.chat.id == USER_CHAT_ID:
        conn = None
        cursor = None
        try:
            logger.info(f"Client send message with chat_id = {USER_CHAT_ID} and message {message.text}")
            euro_rate = float(message.text.replace(',', '.'))
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            id = message.message_id

            conn = mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO euro_rates (id, rate, timestamp) VALUES (%s, %s, %s)", (id, euro_rate, now))
            conn.commit()
            logger.info(f"Save currency {euro_rate}")
        except ValueError:
            await message.reply("Пожалуйста, отправьте корректное число.")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


if __name__ == '__main__':
    from aiogram import executor

    dp.register_message_handler(on_message, content_types=[types.ContentType.TEXT])
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
