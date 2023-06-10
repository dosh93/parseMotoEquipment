from dataclasses import dataclass
from typing import Dict, List

from parsers_api.logger import logger


@dataclass
class LinkImages:
    id_image: str
    id_product_attribute: str


def from_dict_to_dataclass(data: Dict) -> List[LinkImages]:
    return [LinkImages(product["id_image"], product["id_product_attribute"])
            for product_list in data.values()
            for product in product_list]


def process_json_link_images(json_obj):
    logger.info('Processing link_images')
    logger.debug(f'Processing link_images json: {json_obj}')

    link_images = from_dict_to_dataclass(json_obj)

    logger.debug(f'Processing link_images result: {link_images}')
    logger.info('Process link_images end')
    return link_images
