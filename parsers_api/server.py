import configparser
from quart import Quart, request

from logger import configure_logger
from main import add_product_marti_motors, update_price_marti_motors


app = Quart(__name__)

logger = configure_logger(__name__)

config = configparser.ConfigParser()
config.read('config.ini')

host = config.get('flask_app', 'host', fallback='0.0.0.0')
port = config.getint('flask_app', 'port', fallback=8080)


@app.route('/add_product', methods=['GET'])
async def add_product():
    url = request.args.get('url', None)
    if url:
        result = await add_product_marti_motors(url)
        app.logger.info(f'Product with URL "{url}" successfully added')
        return result, 200
    else:
        app.logger.error('URL parameter not provided')
        return 'URL parameter not provided', 400


@app.route('/update_prices', methods=['GET'])
async def update_prices():
    result = await update_price_marti_motors()
    app.logger.debug('Prices of all products successfully updated')
    return f"Update {result} product", 200


@app.route('/update_price', methods=['GET'])
async def update_price():
    url = request.args.get('url', None)
    id_product = request.args.get('id', None)

    if url:
        result = await update_price_marti_motors(url=url)
        app.logger.info(f'Price of the product with URL "{url}" successfully updated')
        return f'Price of the product with URL "{url}" successfully updated', 200
    elif id_product:
        result = await update_price_marti_motors(id_product=id_product)
        app.logger.info(f'Price of the product with ID {id_product} successfully updated')
        return f'Price of the product with ID {id_product} successfully updated', 200
    else:
        app.logger.error('URL or ID parameters not provided')
        return 'URL or ID parameters not provided', 400


if __name__ == '__main__':
    app.run(host=host, port=port)
