import configparser
import os
import schedule
import requests
import time

from common.logger import configure_logger

logger = configure_logger(__name__)


def read_config():
    config = configparser.ConfigParser()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "config.ini")
    config.read(config_path)
    urls = [(config.get('URL', 'url_to_call'), config.get('URL', 'start_time'))]
    url_send_message = config.get('URL', 'url_to_send_message')

    i = 2
    while True:
        try:
            urls.append((config.get(f'URL', f'url_to_call_{i}'), config.get(f'URL', f'start_time_{i}')))
            i += 1
        except configparser.NoOptionError:
            break
    return urls, url_send_message


def call_url(url, url_send_message):
    message = ""
    try:
        response = requests.get(url)
        response.raise_for_status()
        message = f'URL called successfully: {url}. Results: {response.content.decode("utf-8")}'
        logger.info(message)
    except requests.exceptions.RequestException as e:
        message = f'Error calling URL: {e}'
        logger.error(message)
    finally:
        requests.get(url_send_message, params={'text': message, 'service_name': 'service_update_price'})


def job(url, url_send_message):
    call_url(url, url_send_message)


def main():
    urls, url_send_message = read_config()
    for url, start_time in urls:
        schedule.every().day.at(start_time).do(job, url=url, url_send_message=url_send_message)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
