import requests

from parsers_api.logger import logger


def get_price_with_promo(url, id_product_attribute):
    headers = {
        'authority': 'www.martimotos.com',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'ru,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.martimotos.com',
        'referer': url,
        'cookie': 'PrestaShop-990b6adc0296b50eeb235103a6e5b9d5=a9a9e9e5b04262e6c5e680f55f70067421e9ee9be7817ff227ed67f0ce6264d4%3AP8kvxRe61QEUTuuHUbmvm0PCkuqVNoWmL8VEvVkP62PXyea42hX0eBNBWOmXcqxspWVFgLeVl4Bz1x9g%2FjvLS1d8rxtqYVBybcx2JrfwWj0%2Bw5k%2FwtUjUtJCJj8g6Q36%2BEBxEZYwJNuBSOkj6qavRl%2F%2FjaKLZ8mvdCWitKiOJHfrKZ%2BaKMAWn9cffq%2F74HEc%2Bt7GJopgBNFnfXTcIArYHxfTMHlXNuM0IR3C1SI%2BTQ7ZY1VAmC1Ky3BVQyfkBIN48shR8%2BUcwZ%2FmLHURSNdcEBnM4%2BdMHZ9LqqkIMAv4PI0cAI3cYlsC9KYKnDq7%2FoP7FE7nzYNzid8o%2FDiB0PSoWw%3D%3D; PHPSESSID=41nto9vgp7808o87m0fkpcm9i1',
        'sec-ch-ua': '"Chromium";v="112", "YaBrowser";v="23", "Not:A-Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 YaBrowser/23.5.1.714 Yowser/2.5 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    data = {
        'ajax': 'true',
        'getPriceWithPromo': 'true',
        'id_product_attribute': id_product_attribute,
        'checked': 'true'
    }

    response = requests.post(url, headers=headers, data=data)
    logger.info("get_price_with_promo response with %s: %s", id_product_attribute, response.text)

    if response.status_code == 200:
        response_json = response.json()
        return response_json.get('price')

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        response_json = response.json()
        return response_json.get('price')
