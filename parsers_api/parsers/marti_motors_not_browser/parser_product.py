from dataclasses import dataclass
from typing import List

from parsers_api.logger import logger


@dataclass
class AdditionalProperty:
    name: str
    value: str


@dataclass
class Offer:
    price: str
    sku: str
    availability: bool


@dataclass
class Offers:
    offers: List[Offer]


@dataclass
class Product:
    name: str
    description: str
    additionalProperty: List[AdditionalProperty]
    offers: Offers


def from_dict_to_dataclass(data):
    additionalProperties = [
        AdditionalProperty(name=prop.get('name'), value=prop.get('value'))
        for prop in data.get('additionalProperty', [])
    ]
    offers = [
        Offer(
            price=offer.get('price'),
            sku=offer.get('sku'),
            availability=offer.get('availability') == "https://schema.org/InStock"
        )
        for offer in data.get('offers', {}).get('offers', [])
    ]
    offers = Offers(offers)
    return Product(
        name=data.get('name'),
        description=data.get('description'),
        additionalProperty=additionalProperties,
        offers=offers
    )


def process_json_product(json_obj):
    logger.info('Processing product')
    logger.debug(f'Processing product json: {json_obj}')

    product = from_dict_to_dataclass(json_obj)

    logger.debug(f'Processing product result: {product}')
    logger.info('Process product end')
    return product
