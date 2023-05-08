import configparser
import os

import requests
import time
from datetime import datetime, timedelta

from common.logger import configure_logger

logger = configure_logger(__name__)


def read_config():
    config = configparser.ConfigParser()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "config.ini")
    config.read(config_path)
    url = config.get('URL', 'url_to_call')
    interval = config.getint('URL', 'interval')
    start_time = config.get('URL', 'start_time')
    return url, interval, start_time


def call_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        logger.info(f'URL called successfully: {url}. Results: ${response.content}')
    except requests.exceptions.RequestException as e:
        logger.error(f'Error calling URL: {e}')


def time_until_next_run(start_time_str, interval):
    start_time = datetime.strptime(start_time_str, '%H:%M:%S').time()
    now = datetime.now()
    today_start = now.replace(hour=start_time.hour, minute=start_time.minute, second=start_time.second, microsecond=0)
    if now < today_start:
        return (today_start - now).total_seconds()
    else:
        next_start = today_start + timedelta(seconds=interval)
        return (next_start - now).total_seconds()


def main():
    url, interval, start_time = read_config()
    logger.debug(f'Config values: URL={url}, interval={interval}, start_time={start_time}')
    while True:
        time_to_next_run = time_until_next_run(start_time, interval)
        logger.debug(f'Sleeping for {time_to_next_run} seconds')
        time.sleep(time_to_next_run)
        call_url(url)


if __name__ == "__main__":
    main()
