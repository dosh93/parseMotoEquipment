from pony.orm import Database, Required, Set, LongStr, PrimaryKey, Optional, db_session, commit, select
from configparser import ConfigParser

from parsers_api.data.markup import json_to_markup
from parsers_api.logger import logger
import os

db = Database()


class Product(db.Entity):
    _table_ = 'products'
    id = PrimaryKey(int, auto=True)
    url = Required(str)
    id_product = Required(str)
    name_site = Required(str)
    category_id = Required(int)
    last_rate = Required(float)
    last_json_markup = Required(LongStr)


class Category(db.Entity):
    _table_ = 'categories'
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    json_markup = Required(LongStr)


class EuroRate(db.Entity):
    _table_ = 'euro_rates'
    id = PrimaryKey(int)
    rate = Required(float)
    timestamp = Required(str)


class MySQLConnector:

    def __init__(self, config_file='config.ini'):
        config = ConfigParser()
        config_file_path = os.path.join(os.path.dirname(__file__), '..', 'config.ini')
        config.read(config_file_path)

        self.host = config.get('mysql', 'host')
        self.user = config.get('mysql', 'user')
        self.password = config.get('mysql', 'password')
        self.database = config.get('mysql', 'database')

        db.bind(provider='mysql', host=self.host, user=self.user, passwd=self.password, db=self.database)
        db.generate_mapping(create_tables=True)
        logger.debug("MySQLConnector initialized with config file: %s", config_file)

    @db_session
    def save_data(self, url, id_product, name_site, category_id, rate, json_markup):
        try:
            Product(url=url, id_product=id_product, name_site=name_site, category_id=category_id, last_rate=rate,
                    last_json_markup=json_markup)
            db.commit()
            logger.info("Data saved: url=%s, id_product=%s, name_site=%s, category_id=%s", url, id_product, name_site,
                        category_id)
        except Exception as e:
            logger.error("Error saving data: %s", e)

    @db_session
    def get_data_by_id_product(self, id_product):
        logger.info("Fetching data with condition: id_product=%s", id_product)
        data = list(Product.select(lambda p: p.id_product == id_product))
        logger.info("Fetched %d rows", len(data))
        return data

    @db_session
    def get_data_by_url(self, url):
        logger.info("Fetching data with condition: url=%s", url)
        data = list(Product.select(lambda p: p.url == url))
        logger.info("Fetched %d rows", len(data))
        return data

    @db_session
    def update_product_after_update_price(self, product, rate, markup):
        product.last_rate = rate
        product.last_json_markup = markup

    def get_data_where_batch(self, name_site, batch_size=100):
        offset = 0
        while True:
            with db_session:
                data_query = select(p for p in Product if p.name_site == name_site)
                batch = data_query.limit(batch_size, offset=offset)[:]
                if not batch:
                    break
                logger.info("Fetched %d rows", len(batch))
                yield batch
            offset += batch_size

    @db_session
    def delete_by_id(self, id):
        logger.info("Deleting Product with ID: %s", id)
        try:
            Product[id].delete()
            logger.info("Deleted Product with ID: %s", id)
        except Exception as e:
            logger.error("Error deleting Product with ID: %s, %s", id, e)

    @db_session
    def get_currency_rate(self):
        logger.info("Getting latest currency rate")
        try:
            rate = EuroRate.select().order_by(EuroRate.timestamp.desc()).first().rate
            logger.info("Got latest currency rate: %s", rate)
            return rate
        except Exception as e:
            logger.error("Error getting latest currency rate: %s", e)

    @db_session
    def get_markup(self, category_id):
        logger.info("Getting markup for category ID: %s", category_id)
        try:
            category = Category[category_id]
            markup = category.json_markup
            logger.info("Got markup for category ID: %s", category_id)
            logger.debug("Markup for category ID: %s", markup)
            return json_to_markup(markup)
        except Exception as e:
            logger.error("Error getting markup for category ID: %s, %s", category_id, e)

    @db_session
    def get_categories(self):
        logger.info("Getting all categories")
        try:
            categories = list(Category.select().prefetch(Category.json_markup))
            logger.info("Got %s categories", len(categories))
            return categories
        except Exception as e:
            logger.error("Error getting categories: %s", e)

    @db_session
    def get_products_by_ids(self, product_ids):
        logger.info("Getting products by IDs: %s", product_ids)
        try:
            products = select(p for p in Product if p.id_product in product_ids)[:]
            logger.info("Got %s products", len(products))
            return products
        except Exception as e:
            logger.error("Error getting products with ids: %s", e)
