from db_conn.my_sql_connector import MySQLConnector
from parsers.marti_motors.helper import get_variants, get_variant_with_price, get_media
from parsers.marti_motors.marti_motors_parser import parse_by_url
from wix.site_items import WixItem
from wix.wix_api import WixAPI

api = WixAPI()
db = MySQLConnector()
db.create_table()


async def add_product_marti_motors(url):
    item = await parse_by_url(url)

    product_to_wix = WixItem(item["name"], item["one_price"], item["description"], get_variants(item),
                             get_variant_with_price(item), get_media(item))

    result = api.add_product(product_to_wix)
    api.add_variants(result["id"], product_to_wix.variantOptions)
    api.add_media(result["id"], product_to_wix.media)

    db.save_data(item["base_url"], result["id"], "martimotos")
    return result


async def update_price_marti_motors(id_product=None, url=None):
    if id_product is not None:
        products = db.get_data_where({"id_product": id_product})
    elif url is not None:
        products = db.get_data_where({"url": url})
    else:
        products = db.get_data_where({"name_site": "martimotos"})

    count_update_product = 0
    for product in products:
        product_id = product[2]
        item = await parse_by_url(product[1])
        product_to_wix = WixItem(item["name"], item["one_price"], item["description"], get_variants(item),
                                 get_variant_with_price(item), get_media(item))
        api.reset_all_variant(product_id)
        api.update_product(product_to_wix, product_id)
        api.add_variants(product_id, product_to_wix.variantOptions)
        api.delete_media(product_id)
        api.add_media(product_id, product_to_wix.media)
        count_update_product += 1
    return count_update_product