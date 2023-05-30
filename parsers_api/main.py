from db_conn.my_sql_connector import MySQLConnector
from parsers.marti_motors.helper import get_variants, get_variant_with_price, get_media
from parsers.marti_motors.marti_motors_parser import parse_by_url
from parsers_api.currency_rate import CurrencyRate
from parsers_api.data.markup import json_to_markup

from wix.site_items import WixItem
from wix.wix_api import WixAPI
from parsers_api.logger import logger

api = WixAPI()
db = MySQLConnector()
db.create_table()


def is_duplicate(url):
    return len(db.get_data_where({"url": url})) != 0


async def add_product_marti_motors(url, category_id):
    rate = CurrencyRate.get_rate_db()
    markups = db.get_markup(category_id)

    item = await parse_by_url(url, rate, markups)

    product_to_wix = WixItem(item["name"], item["one_price"], item["description"], get_variants(item),
                             get_variant_with_price(item), get_media(item))

    result = api.add_product(product_to_wix)
    api.add_variants(result["id"], product_to_wix.variantOptions)
    api.add_media(result["id"], product_to_wix.media)

    db.save_data(item["base_url"], result["id"], "martimotos", category_id)
    return result


async def update_price_marti_motors(id_product=None, url=None):
    rate = CurrencyRate.get_rate_db()
    categories = db.get_categories()
    count_update_product = 0

    if id_product is not None:
        condition = {"id_product": id_product}
    elif url is not None:
        condition = {"url": url}
    else:
        condition = {"name_site": "martimotos"}

    if id_product is None and url is None:
        data_generator = db.get_data_where_batch(condition)
        for batch in data_generator:
            for product in batch:
                markups = get_markup_by_category_id(categories, product[4])
                await update_one_product_martimotos(product, rate, markups)
                count_update_product += 1
    else:
        products = db.get_data_where(condition)
        count_update_product = await update_all_product_martimotos(products, rate, categories)

    return count_update_product


async def update_all_product_martimotos(products, rate, categories):
    count_update_product = 0
    for product in products:
        markups = get_markup_by_category_id(categories, product[4])
        await update_one_product_martimotos(product, rate, markups)
        count_update_product += 1
    return count_update_product


async def update_one_product_martimotos(product, rate, markups):
    logger.info(f"Product {product}")
    product_id = product[2]
    code = api.get_product(product_id).status_code
    if code == 404:
        logger.info(f"Product with id {product_id} not found in wix")
        db.delete_by_id(product[0])
    elif code == 200:
        item = await parse_by_url(product[1], rate, markups)
        product_to_wix = WixItem(item["name"], item["one_price"], item["description"], get_variants(item),
                                 get_variant_with_price(item), get_media(item))
        api.reset_all_variant(product_id)
        api.update_product(product_to_wix, product_id)
        api.add_variants(product_id, product_to_wix.variantOptions)
        api.delete_media(product_id)
        api.add_media(product_id, product_to_wix.media)


async def get_categories_main():
    return db.get_categories()


def get_markup_by_category_id(categories, category_id):
    for category in categories:
        if category.id == category_id:
            return json_to_markup(category.markup)
