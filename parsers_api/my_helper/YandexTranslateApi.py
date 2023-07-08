import configparser
import os

import requests
import datetime
from parsers_api.logger import logger
from typing import Optional


class YandexTranslateApi:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config_file_path = os.path.join(os.path.dirname(__file__), '..', 'config.ini')
        self.config.read(self.config_file_path)
        self.oauth_token = self.config.get('yandex', 'oauth_token')
        self.folder_id = self.config.get('yandex', 'folder_id')
        self.token_expiry = datetime.datetime.now()
        self.iam_token: Optional[str] = None

    def authenticate(self):
        if datetime.datetime.now() > self.token_expiry or self.iam_token is None:
            headers = {'Content-Type': 'Application/json'}
            data = {"yandexPassportOauthToken": self.oauth_token}
            response = requests.post('https://iam.api.cloud.yandex.net/iam/v1/tokens', headers=headers, json=data)
            response_data = response.json()
            self.iam_token = response_data['iamToken']
            expiry_date = response_data['expiresAt']
            expiry_date = expiry_date[:23] + 'Z'
            self.token_expiry = datetime.datetime.strptime(expiry_date, '%Y-%m-%dT%H:%M:%S.%fZ')
            logger.info('Authenticated successfully. Token will expire at %s', self.token_expiry)
        else:
            logger.debug('Token is still valid, no need to authenticate')

    def translate(self, source_language_code, target_language_code, text, format='HTML'):
        self.authenticate()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.iam_token}"
        }
        body = {
            "sourceLanguageCode": source_language_code,
            "targetLanguageCode": target_language_code,
            "texts": [text],
            "folderId": self.folder_id,
            "format": format
        }
        response = requests.post('https://translate.api.cloud.yandex.net/translate/v2/translate',
                                 headers=headers, json=body)
        response_data = response.json()
        translated_text = response_data['translations'][0]['text']
        logger.debug('Translation completed: %s', translated_text)
        return translated_text
