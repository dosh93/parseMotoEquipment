import json
from dataclasses import dataclass
from typing import Dict

from parsers_api.logger import logger


@dataclass
class Attribute:
    reference: str
    attributes_values: Dict[str, str]
    id_product_attribute: str


def extract_required_fields(json_dict: Dict[str, Dict]):
    return {
        key: {
            'reference': value.get('reference'),
            'attributes_values': value.get('attributes_values'),
            'id_product_attribute': value.get('specific_price').get('id_product_attribute')
            if value.get('specific_price') else None
        }
        for key, value in json_dict.items()
        if value.get('reference') and value.get('attributes_values') and value.get('specific_price')
    }


def process_json_attributes(json_obj):
    logger.info('Processing attributes')
    logger.debug(f'Processing attributes json: {json_obj}')

    filtered_dict = extract_required_fields(json_obj)

    attributes = {key: Attribute(**value) for key, value in filtered_dict.items()}
    logger.debug(f'Processing attributes result: {attributes}')
    logger.info('Process attributes end')
    return attributes
