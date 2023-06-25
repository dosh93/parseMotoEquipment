import json

import requests

from parsers_api.logger import logger
from bs4 import BeautifulSoup

from parsers_api.parsers.marti_motors_not_browser.helper import get_images, get_description, get_prices, get_one_price, \
    get_photo_by_color, get_all_data_for_parse, get_min_price_eur, get_page_count, get_product_links_and_names
from parsers_api.parsers.marti_motors_not_browser.parser_attributes import process_json_attributes
from parsers_api.parsers.marti_motors_not_browser.parser_product import process_json_product
from parsers_api.parsers.marti_motors_not_browser.parser_link_images import process_json_link_images


def parse_by_url(url, rate, markups):
    try:
        logger.info(f"Start parse by url {url}")
        response = requests.get(url)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        images = get_images(soup)

        json_objects = get_all_data_for_parse(soup)
        attributes = process_json_attributes(json_objects['attributes'])
        product = process_json_product(json_objects['product'])
        link_images = process_json_link_images(json_objects['link_images'])

        item = {"name": product.name, "base_url": url, "price": get_prices(product, attributes, rate, markups, url),
                "photos": list(images.values()),
                "photoByColor": get_photo_by_color(attributes, images, link_images),
                "description": get_description(product)}
        item["one_price"] = get_one_price(item["price"])
        item["min_price_eur"] = get_min_price_eur(item["price"])
        logger.info(f"Done parse {url}")
        logger.debug(f"json: \n{json.dumps(item, indent=2)}")
        return item
    except Exception as e:
        logger.error(f"Error parsing {e}")


def parse_outlets():
    base_url = "https://www.martimotos.com/es/outlet-moto?p=1"
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, 'lxml')
    page_count = get_page_count(soup)
    logger.info(f"Count page in outlet: {page_count}")

    for i in range(1, page_count + 1):
        logger.info(f"Start parse page: {i}")
        response = requests.get(base_url.replace("p=1", f"p={i}"))
        soup = BeautifulSoup(response.content, 'lxml')
        products = get_product_links_and_names(soup)
        logger.info(f"End parse page: {i}. Count product on page: {len(products)}")
        yield products
