import logging
from logging.handlers import TimedRotatingFileHandler
import configparser
import os

def configure_logger(logger_name):

    config = configparser.ConfigParser()
    config_file_path = os.path.join(os.path.dirname(__file__), '', 'config.ini')
    config.read(config_file_path)

    log_filename = config.get('logging', 'log_filename')
    interval = config.getint('logging', 'interval')
    backup_count = config.getint('logging', 'backup_count')
    log_level = config.get('logging', 'log_level')
    log_format = config.get('logging', 'log_format')
    console_logging = config.getboolean('logging', 'console_logging')

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.getLevelName(log_level))

    file_handler = TimedRotatingFileHandler(log_filename, when='midnight', interval=interval, backupCount=backup_count)
    file_handler.setLevel(logging.getLevelName(log_level))

    formatter = logging.Formatter(f'{log_format} - [%(filename)s:%(lineno)d]')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    if console_logging:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.getLevelName(log_level))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
