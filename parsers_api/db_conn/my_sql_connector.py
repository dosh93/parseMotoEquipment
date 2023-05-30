import os

import mysql.connector
from configparser import ConfigParser

from parsers_api.data.category import db_to_category
from parsers_api.data.markup import json_to_markup

from parsers_api.logger import logger


class MySQLConnector:

    def __init__(self, config_file='config.ini'):
        config = ConfigParser()
        config_file_path = os.path.join(os.path.dirname(__file__), '..', 'config.ini')
        config.read(config_file_path)

        self.host = config.get('mysql', 'host')
        self.user = config.get('mysql', 'user')
        self.password = config.get('mysql', 'password')
        self.database = config.get('mysql', 'database')

        self.conn = self.connect()
        logger.debug("MySQLConnector initialized with config file: %s", config_file)

    def __del__(self):
        self.close()

    def connect(self):
        try:
            conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            logger.info("Connected to MySQL database")
            return conn
        except mysql.connector.Error as e:
            logger.error("Error connecting to MySQL database: %s", e)
            return None

    def close(self):
        self.conn.close()
        logger.info("MySQL connection closed")

    def create_table(self):
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    url VARCHAR(255) NOT NULL,
                    id_product VARCHAR(255) NOT NULL,
                    name_site  VARCHAR(255) NOT NULL,
                    category_id INT NOT NULL
                )
            ''')
            logger.info("Table 'products' created or already exists")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    json_markup TEXT NOT NULL
                )
            ''')
            logger.info("Table 'categories' created or already exists")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS euro_rates (
                    id INT PRIMARY KEY,
                    rate FLOAT NOT NULL,
                    timestamp DATETIME NOT NULL
                )    
            ''')
            logger.info("Table 'euro_rates' created or already exists")
        except mysql.connector.Error as e:
            logger.error("Error creating table 'products': %s", e)
        finally:
            cursor.close()

    def save_data(self, url, id_product, name_site, category_id):
        cursor = self.conn.cursor()
        try:
            query = "INSERT INTO products (url, id_product, name_site, category_id) VALUES (%s, %s, %s, %s)"
            values = (url, id_product, name_site, category_id)
            cursor.execute(query, values)
            self.conn.commit()
            logger.info("Data saved: url=%s, id_product=%s, name_site=%s, category_id=%s", url, id_product, name_site,
                        category_id)
        except mysql.connector.Error as e:
            logger.error("Error saving data: %s", e)
        finally:
            cursor.close()

    def get_data_where(self, where_conditions=None):
        cursor = self.conn.cursor()
        try:
            query = "SELECT * FROM products"
            if where_conditions:
                conditions = []
                args = []
                for column, value in where_conditions.items():
                    conditions.append(f"{column} = %s")
                    args.append(value)
                query += " WHERE " + " AND ".join(conditions)

                if args:
                    cursor.execute(query, args)
                else:
                    cursor.execute(query)

            logger.info(f"query = {query}")
            rows = cursor.fetchall()
            logger.info("Data fetched with WHERE clause: %d rows", len(rows))
            return rows
        except mysql.connector.Error as e:
            logger.error("Error fetching data with WHERE clause: %s", e)
            rows = []
        finally:
            cursor.close()

    def get_data_where_batch(self, where_conditions=None, batch_size=50):
        cursor = self.conn.cursor()
        try:
            query = "SELECT * FROM products"
            if where_conditions:
                conditions = []
                args = []
                for column, value in where_conditions.items():
                    conditions.append(f"{column} = %s")
                    args.append(value)
                query += " WHERE " + " AND ".join(conditions)

                if args:
                    cursor.execute(query, args)
                else:
                    cursor.execute(query)

            logger.info(f"query = {query}")

            while True:
                rows = cursor.fetchmany(batch_size)
                if not rows:
                    break

                logger.info("Data fetched with WHERE clause: %d rows", len(rows))
                yield rows
        except mysql.connector.Error as e:
            logger.error("Error fetching data with WHERE clause: %s", e)
            rows = []
        finally:
            cursor.close()

    def delete_by_id(self, id):
        cursor = self.conn.cursor()
        try:
            query = "DELETE FROM products WHERE id = %s"
            values = (id,)
            cursor.execute(query, values)
            self.conn.commit()
            logger.info("Data deleted: id=%s", id)
        except mysql.connector.Error as e:
            logger.error("Error deleting data by ID: %s", e)
        cursor.close()

    def get_currency_rate(self):
        cursor = self.conn.cursor()
        try:
            query = "SELECT rate FROM euro_rates ORDER BY timestamp DESC LIMIT 1"
            cursor.execute(query)
            rows = cursor.fetchone()
            if rows is not None:
                logger.info(f"Get rate: {rows[0]}")
                return rows[0]
            else:
                logger.warn(f"Rate euro table is empty")
            return None
        except mysql.connector.Error as e:
            logger.error(f"Error getting rate {e}")
        finally:
            cursor.close()

    def get_markup(self, category_id):
        cursor = self.conn.cursor()
        try:
            query = "SELECT * FROM categories WHERE id = %s"
            values = (category_id,)
            cursor.execute(query, values)
            rows = cursor.fetchone()
            if rows is not None:
                logger.info(f"Get category by id: {rows[0]}")
                return json_to_markup(rows[2])
            else:
                logger.warn(f"Not exist category")
            return None
        except mysql.connector.Error as e:
            logger.error(f"Error getting category {e}")
        finally:
            cursor.close()

    def get_categories(self):
        cursor = self.conn.cursor()
        try:
            query = "SELECT * FROM categories"
            cursor.execute(query)

            logger.info(f"query = {query}")
            rows = cursor.fetchall()
            logger.info(f"Get categories {len(rows)}", )
            return db_to_category(rows)
        except mysql.connector.Error as e:
            logger.error("Error get categories: %s", e)
            rows = []
        finally:
            cursor.close()
