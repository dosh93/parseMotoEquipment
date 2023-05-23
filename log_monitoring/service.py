import os
import requests
import schedule
import time
import configparser

from common.logger import configure_logger

logger = configure_logger(__name__)

config = configparser.ConfigParser()
current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_dir, "config.ini")

config.read(config_path)
log_dir = config.get('Settings', 'LogDir')
log_filename = config.get('Settings', 'LogFilename')
host = config.get('Settings', 'Host')
port = config.get('Settings', 'Port')

log_positions = {}
log_details = {}


def check_logs():
    for root, dirs, files in os.walk(log_dir):
        if log_filename in files:
            log_path = os.path.join(root, log_filename)
            new_file = False
            if log_path not in log_details:
                log_details[log_path] = (os.path.getsize(log_path), os.path.getmtime(log_path))
                log_positions[log_path] = 0
                new_file = True

            file_size = os.path.getsize(log_path)
            file_mtime = os.path.getmtime(log_path)

            # Проверка, был ли файл изменен с момента последнего чтения
            if file_size != log_details[log_path][0] or file_mtime != log_details[log_path][1] or new_file:
                log_details[log_path] = (file_size, file_mtime)
                error_lines = []
                folder_name = os.path.basename(root)  # Название папки
                with open(log_path, 'r', encoding='utf-8') as log_file:
                    log_file.seek(log_positions[log_path])
                    for line in log_file:
                        if 'error' in line.lower():  # Поиск строки с ошибкой
                            error_lines.append(line)
                    log_positions[log_path] = log_file.tell()

                if error_lines:
                    text = '\n'.join(error_lines)
                    requests.get(f'{host}:{port}/send_message',
                                 params={'text': f'Folder: {folder_name}, Error:\n{text}',
                                         'service_name': 'log_monitoring'})

            logger.info(f'Checked log file: {log_path}')


schedule.every().minute.do(check_logs)
logger.info(f'Starting')
while True:
    schedule.run_pending()
    time.sleep(1)
