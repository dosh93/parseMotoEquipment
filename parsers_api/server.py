import configparser
from quart import Response
import os

from quart import Quart, request

from main import add_product_marti_motors, update_price_marti_motors, is_duplicate, get_categories_main
from parsers_api.logger import logger

app = Quart(__name__)


config = configparser.ConfigParser()
current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_dir, "config.ini")

config.read(config_path)

host = config.get('flask_app', 'host', fallback='0.0.0.0')
port = config.getint('flask_app', 'port', fallback=8080)


@app.route('/add_product', methods=['GET'])
async def add_product():
    url = request.args.get('url', None)
    category_id = request.args.get('category_id', None)
    if is_duplicate(url):
        return f"Такой товар уже есть", 409
    if url:
        result = add_product_marti_motors(url, category_id)
        logger.info(f'Product with URL "{url}" successfully added')
        product_url = result['productPageUrl']["base"] + result['productPageUrl']["path"]
        return f"Добавлен продукт. Вот ссылка {product_url}", 200
    else:
        logger.error('URL parameter not provided')
        return 'URL parameter not provided', 400


@app.route('/get_categories', methods=['GET'])
async def get_categories():
    logger.info(f'Get categories')
    categories = get_categories_main()
    return Response(categories, mimetype='application/json')


@app.route('/update_prices', methods=['GET'])
async def update_prices():
    try:
        result, errors = update_price_marti_motors()
        logger.debug('Prices of all products successfully updated')
        if len(errors) != 0:
            logger.warning(f'Not updated products with ids {errors}')
        return f"Обновлено продуктов: {result}. С ошибками {errors}", 200
    except Exception as e:
        return f"Что-то пошло не так: {e}", 500


@app.route('/update_price', methods=['GET'])
async def update_price():
    url = request.args.get('url', None)
    id_product = request.args.get('id', None)

    if url:
        result = update_price_marti_motors(url=url)
        logger.info(f'Price of the product with URL "{url}" successfully updated')
        return f'Обновлено продуктов: {result}', 200
    elif id_product:
        result = update_price_marti_motors(id_product=id_product)
        logger.info(f'Price of the product with ID {id_product} successfully updated')
        return f'Обновлено продуктов: {result}', 200
    else:
        logger.error('URL or ID parameters not provided')
        return 'URL or ID parameters not provided', 400


if __name__ == '__main__':
    app.run(host=host, port=port)
