import configparser
import json
import os

import requests

from parsers_api.logger import logger
from parsers_api.wix.site_items import get_product_for_update_description


class WixAPI:
    def __init__(self):
        self.config = configparser.ConfigParser()
        config_file_path = os.path.join(os.path.dirname(__file__), '..', 'config.ini')
        self.config.read(config_file_path)
        self.url = self.config['wix']['url']
        self.headers = {
            'Authorization': self.config['wix']['token'],
            'wix-site-id': self.config['wix']['wix_site_id']
        }

    def __post(self, endpoint, data=None):
        try:
            response = requests.post(self.url + endpoint, json=data, headers=self.headers)
            logger.info(f"POST request sent to {self.url + endpoint}")
            logger.debug(f"POST response: {response.status_code} {response.content} ")
            return json.loads(response.content)
        except Exception as e:
            logger.error(f"Error occurred while sending POST request: {e}")
            return None

    def __patch(self, endpoint, data=None):
        try:
            response = requests.patch(self.url + endpoint, json=data, headers=self.headers)
            logger.info(f"PATCH request sent to {self.url + endpoint}")
            logger.debug(f"PATCH response: {response.status_code} {response.content} ")
            return json.loads(response.content)
        except Exception as e:
            logger.error(f"Error occurred while sending PATCH request: {e}")
            return None

    def __get(self, endpoint):
        try:
            response = requests.get(self.url + endpoint, headers=self.headers)
            logger.info(f"GET request sent to {self.url + endpoint}")
            logger.debug(f"GET response: {response.status_code} {response.content} ")
            return response
        except Exception as e:
            logger.error(f"Error occurred while sending GET request: {e}")
            return None

    def add_product(self, product):
        logger.info(f"Adding product {product.product['product']['name']}")
        logger.debug(f"Product {product.product}")
        result = self.__post("/stores/v1/products", product.product)
        if result is not None:
            logger.info(f"Add product {result['product']['name']} successfully with id {result['product']['id']}")
            return {
                "id": result['product']["id"],
                "productPageUrl": result['product']["productPageUrl"]
            }
        else:
            logger.warning(f"Add product {product.product['product']['name']} failed")
            return None

    def update_product(self, product, id_product):
        logger.info(f"Updating product {product.product['product']['name']}")
        logger.debug(f"Product {product.product}")
        result = self.__patch(f"/stores/v1/products/{id_product}", product.get_product_for_update())
        if result is not None:
            logger.info(f"Update product {result['product']['name']} successfully with id {id_product}")
            return {
                "id": result['product']["id"],
                "productPageUrl": result['product']["productPageUrl"]
            }
        else:
            logger.warning(f"Update product {product.product['product']['name']} failed")
            return None

    def update_description(self, description, id_product):
        logger.info(f"Updating product description {id_product}")
        logger.debug(f"Product description {description}")
        result = self.__patch(f"/stores/v1/products/{id_product}", get_product_for_update_description(description))
        if result is not None:
            logger.info(f"Update product description successfully with id {id_product}")
        else:
            logger.warning(f"Update product description {id_product} failed")

    def add_variants(self, id_product, variants):
        logger.info(f"Adding variants to product with id {id_product}")
        logger.debug(f"Variants {json.dumps(variants, ensure_ascii=False, indent=2)}")
        result = self.__patch(f"/stores/v1/products/{id_product}/variants", variants)
        if result is not None:
            logger.info(f"Add variants successfully with id {id_product}")
            return True
        else:
            logger.warning(f"Add variants to product with id {id_product} failed")
            return None

    def add_media(self, id_product, media):
        logger.info(f"Adding media to product with id {id_product}")
        logger.debug(f"Media {json.dumps(media, ensure_ascii=False, indent=2)}")
        result = self.__post(f"/stores/v1/products/{id_product}/media", media)
        if result is not None:
            logger.info(f"Add media successfully with id {id_product}")
            return True
        else:
            logger.warning(f"Add media to product with id {id_product} failed")
            return None

    def delete_media(self, id_product):
        logger.info(f"Deleting media product with id {id_product}")
        result = self.__post(f"/stores/v1/products/{id_product}/media/delete")
        if result is not None:
            logger.info(f"Delete media successfully with id {id_product}")
            return True
        else:
            logger.warning(f"Delete media to product with id {id_product} failed")
            return None

    def reset_all_variant(self, id_product):
        logger.info(f"Resetting all variant product with id {id_product}")
        result = self.__post(f"/stores/v1/products/{id_product}/variants/resetToDefault")
        if result is not None:
            logger.info(f"Reset all variants product successfully with id {id_product}")
            return result
        else:
            logger.warning(f"Reset all variants product with id {id_product} failed")
            return None

    def get_product(self, id_product):
        logger.info(f"Get product with id {id_product}")
        result = self.__get(f"/stores/v1/products/{id_product}")
        if result is not None:
            logger.info(f"Get product with id {id_product} successfully")
            return result
        else:
            logger.warning(f"Get product with id {id_product} failed")
            return None


