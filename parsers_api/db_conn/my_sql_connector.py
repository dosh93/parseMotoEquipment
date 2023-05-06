import os

import mysql.connector
from configparser import ConfigParser

from common.logger import configure_logger

logger = configure_logger(__name__)


class MySQLConnector:

    def __init__(self, config_file='config.ini'):
        config = ConfigParser()
        config_file_path = os.path.join(os.path.dirname(__file__), '..', 'config.ini')
        config.read(config_file_path)

        self.host = config.get('mysql', 'host')
        self.user = config.get('mysql', 'user')
        self.password = config.get('mysql', 'password')
        self.database = config.get('mysql', 'database')

        logger.debug("MySQLConnector initialized with config file: %s", config_file)

    def connect(self):
        try:
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.conn.cursor()
            logger.info("Connected to MySQL database")
        except mysql.connector.Error as e:
            logger.error("Error connecting to MySQL database: %s", e)

    def close(self):
        self.conn.close()
        logger.info("MySQL connection closed")

    def create_table(self):
        self.connect()
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    url VARCHAR(255) NOT NULL,
                    id_product VARCHAR(255) NOT NULL,
                    name_site  VARCHAR(255) NOT NULL
                )
            ''')
            logger.info("Table 'products' created or already exists")
        except mysql.connector.Error as e:
            logger.error("Error creating table 'products': %s", e)
        self.close()

    def save_data(self, url, id_product, name_site):
        self.connect()
        try:
            query = "INSERT INTO products (url, id_product, name_site) VALUES (%s, %s, %s)"
            values = (url, id_product, name_site)
            self.cursor.execute(query, values)
            self.conn.commit()
            logger.info("Data saved: url=%s, id_product=%s, name_site=%s", url, id_product, name_site)
        except mysql.connector.Error as e:
            logger.error("Error saving data: %s", e)
        self.close()

    def get_data_where(self, where_conditions=None):
        self.connect()
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
                    self.cursor.execute(query, args)
                else:
                    self.cursor.execute(query)

            logger.info(f"query = {query}")
            rows = self.cursor.fetchall()
            logger.info("Data fetched with WHERE clause: %d rows", len(rows))
        except mysql.connector.Error as e:
            logger.error("Error fetching data with WHERE clause: %s", e)
            rows = []
        self.close()
        return rows
