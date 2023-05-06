import configparser
import os

import requests
import time
from datetime import datetime, timedelta


def read_config():
    config = configparser.ConfigParser()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "config.ini")
    return config.get('URL', 'url_to_call')


def call_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        print(f'URL called successfully: {url}')
    except requests.exceptions.RequestException as e:
        print(f'Error calling URL: {e}')


def main():
    url = read_config()
    while True:
        call_url(url)
        now = datetime.now()
        next_day = now + timedelta(days=1)
        next_day = next_day.replace(hour=0, minute=0, second=0, microsecond=0)
        seconds_until_next_day = (next_day - now).total_seconds()
        time.sleep(seconds_until_next_day)


if __name__ == "__main__":
    main()
