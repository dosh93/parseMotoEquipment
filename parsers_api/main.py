import json

from db_conn.my_sql_connector import MySQLConnector
from parsers.marti_motors.helper import get_variants, get_variant_with_price, get_media
from parsers.marti_motors_not_browser.marti_motors_parser import parse_by_url
from parsers_api.currency_rate import CurrencyRate
from parsers_api.data.markup import json_to_markup, markup_to_json
from parsers_api.my_helper.helpers import send_service_message
from parsers_api.parsers.marti_motors_not_browser.helper import get_new_size, get_new_price

from wix.site_items import WixItem
from wix.wix_api import WixAPI
from parsers_api.logger import logger

api = WixAPI()
db = MySQLConnector()


def is_duplicate(url):
    return len(db.get_data_by_url(url)) != 0


def add_product_marti_motors(url, category_id):
    rate = CurrencyRate.get_rate_db()
    markups = db.get_markup(category_id)

    item = parse_by_url(url, rate, markups)

    product_to_wix = WixItem(item["name"], item["one_price"], item["description"], get_variants(item),
                             get_variant_with_price(item), get_media(item))

    result = api.add_product(product_to_wix)
    api.add_variants(result["id"], product_to_wix.variantOptions)
    api.add_media(result["id"], product_to_wix.media)

    db.save_data(item["base_url"], result["id"], "martimotos", category_id, rate, markup_to_json(markups))
    return result


def update_price_marti_motors(id_product=None, url=None):
    rate = CurrencyRate.get_rate_db()
    categories = db.get_categories()
    count_update_product = 0
    error_products = []
    new_size = []
    new_price = []

    if id_product is None and url is None:
        data_generator = db.get_data_where_batch("martimotos")
        for batch in data_generator:
            for product in batch:
                markups = get_markup_by_category_id(categories, product.category_id)
                result = update_one_product_martimotos(product, rate, markups, new_size, new_price)
                if result is not None:
                    error_products.append(result)
                else:
                    count_update_product += 1
        products = db.get_products_by_ids(error_products)
        new_count_update, error_products = update_products(products, rate, categories, new_size, new_price)
        count_update_product += new_count_update
    else:
        products = None
        if id_product is not None:
            products = db.get_data_by_id_product(id_product)
        else:
            products = db.get_data_by_url(url)

        count_update_product, result = update_all_product_martimotos(products, rate, categories, new_size, new_price)
        error_products.append(result)
    if len(new_size) > 0:
        send_service_message(new_size, "new_size")
    if len(new_price) > 0:
        send_service_message(new_price, "new_price")
    return count_update_product, error_products


def update_all_product_martimotos(products, rate, categories, new_size, new_price):
    count_update_product, error_products = update_products(products, rate, categories, new_size, new_price)
    if error_products:
        products = db.get_products_by_ids(error_products)
        new_count_update, error_products = update_products(products, rate, categories, new_size, new_price)
        count_update_product += new_count_update
    return count_update_product, error_products


def update_products(products, rate, categories, new_size, new_price):
    count_update_product = 0
    error_products = []
    for product in products:
        markups = get_markup_by_category_id(categories, product.category_id)
        result = update_one_product_martimotos(product, rate, markups, new_size, new_price)
        if result is not None:
            error_products.append(result)
        else:
            count_update_product += 1
    return count_update_product, error_products


def update_one_product_martimotos(product, rate, markups, new_size, new_price):
    try:
        logger.info(f"Product {product}")
        product_id = product.id_product
        result_product_wix = api.get_product(product_id)
        code = result_product_wix.status_code
        if code == 404:
            logger.info(f"Product with id {product_id} not found in wix")
            db.delete_by_id(product.id)
        elif code == 200:
            item = parse_by_url(product.url, rate, markups)
            product_to_wix = WixItem(item["name"], item["one_price"], item["description"], get_variants(item),
                                     get_variant_with_price(item), get_media(item))
            api.reset_all_variant(product_id)
            api.update_product(product_to_wix, product_id)
            api.add_variants(product_id, product_to_wix.variantOptions)
            last_rate = product.last_rate
            last_markups = json_to_markup(product.last_json_markup)
            db.update_product_after_update_price(product, rate, markup_to_json(markups))
            current_new_price = get_new_price(result_product_wix.json(), last_rate, last_markups, item, rate, markups)
            current_new_size = get_new_size(result_product_wix.json(), item)
            if len(current_new_size) > 0:
                new_size.append({
                    "name": item["name"],
                    "url": product.url,
                    "new_size": current_new_size
                })

            if len(current_new_price) > 0:
                new_price.append({
                    "name": item["name"],
                    "url": product.url,
                    "new_price": current_new_price
                })
    except Exception as e:
        logger.error(f"Error update product: {product} {e}")
        return product.id_product


def get_categories_main():
    logger.info("Starting get categories")
    categories = db.get_categories()
    categories_list = [c.to_dict() for c in categories]
    return json.dumps(categories_list, ensure_ascii=False)


def get_markup_by_category_id(categories, category_id):
    for category in categories:
        if category.id == category_id:
            return json_to_markup(category.json_markup)
