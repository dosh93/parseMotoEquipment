import json
import re

from parsers_api.data.markup import apply_markup, remove_markup
from parsers_api.logger import logger
from parsers_api.my_helper.helpers import get_price_rub
from parsers_api.parsers.common_marti_motors.common import get_price_with_promo
from collections import defaultdict
from itertools import groupby


def extract_json_objects(text, decoder=json.JSONDecoder()):
    """Generate all JSON objects in a string."""
    pos = 0
    while True:
        match = text.find('{', pos)
        if match == -1:
            break
        try:
            result, index = decoder.raw_decode(text[match:])
            yield result
            pos = match + index
        except json.JSONDecodeError:
            pos = match + 1


def is_json_object_of_interest(obj):
    if all(key.isdigit() for key in obj.keys()) and "attributes_values" in list(obj.values())[0]:
        return "attributes"
    elif all(key.isdigit() for key in obj.keys()) and isinstance(list(obj.values())[0], list) and "id_image" in \
            list(obj.values())[0][0]:
        return "link_images"
    elif "name" in obj and "image" in obj and "url" in obj and "@type" in obj and obj["@type"] == "Product":
        return "product"
    else:
        return None


def remove_non_printable_characters(text):
    pattern = r'[^\x20-\x7E]'
    return re.sub(pattern, '', text)


def get_images(soup):
    logger.info('Processing get_images')
    a_tags = soup.find_all('a', class_='fancybox')
    num_link_map = {}

    for a_tag in a_tags:
        href = a_tag.get('href', '')
        img_tag = a_tag.find('img')
        if img_tag:
            img_class = img_tag.get('class', '')
            numbers = [re.findall(r'\d+', c) for c in img_class if 'thumb_' in c]
            for number in numbers:
                if number:
                    num_link_map[number[0]] = href
    logger.info('Process end of get_images')
    return num_link_map


def get_spec(product):
    specification = {}
    for additionalProperty in product.additionalProperty:
        name = additionalProperty.name
        value = additionalProperty.value
        if name in specification:
            specification[name] += " " + value
        else:
            specification[name] = value
    return specification


def get_description(product):
    description_text = product.description
    description_text += "\n"
    spec = get_spec(product)
    if len(spec) > 0:
        description_text += "<ul>"
    for key, value in spec.items():
        description_text += f"<li><strong>{key}</strong> - {value}</li>\n"
    if len(spec) > 0:
        description_text += "</ul>"
    return description_text


def get_prices(product, attributes, rate, markups, url):
    return [
        {
            **({'sku': offer.sku} if offer.availability else {}),
            'price': get_price_rub(apply_markup(price_eur, markups, url), rate) if offer.availability else 0,
            'price_eur': price_eur if offer.availability else 0,
            'isExist': offer.availability,
            'color_name': attr.attributes_values['1'],
            'size_name': attr.attributes_values['2']
        }
        for offer in product.offers.offers
        if (attr := get_attribute(offer.sku, attributes)) and
           (price_eur := get_price_with_promo(url, attr.id_product_attribute)) is not None
    ]


def get_attribute(sku, attributes):
    for attr in attributes.values():
        if attr.reference == sku:
            return attr


def get_one_price(prices):
    for price_dict in prices:
        price = int(price_dict['price'])
        if price != 0:
            return price


def get_photo_by_color(attributes, images, link_images):
    colors_with_id_product_att = get_colors_with_ids_product_attr(attributes)
    colors_with_id_image = get_ids_images_by_color(colors_with_id_product_att, link_images)
    result = []
    for color, ids_image in colors_with_id_image.items():
        result.append({
            'color': color,
            'photos': [images[id_image] for id_image in images.keys() if id_image in ids_image]
        })
    return result


def get_colors_with_ids_product_attr(attributes):
    result = defaultdict(list)
    for attr in attributes.values():
        name_color = attr.attributes_values['1']
        result[name_color].append(attr.id_product_attribute)
    return result


def get_ids_images_by_color(colors_with_id_product_att, link_images):
    result = defaultdict(set)

    id_to_images = defaultdict(set)
    for link in link_images:
        id_to_images[link.id_product_attribute].add(link.id_image)

    for key, value_list in colors_with_id_product_att.items():
        for value in value_list:
            if value in id_to_images:
                result[key].update(id_to_images[value])

    return result


def get_all_data_for_parse(soup):
    json_objects = {
        "attributes": None,
        "link_images": None,
        "product": None
    }
    script_tags = soup.find_all('script')

    for i, script_tag in enumerate(script_tags):
        if not script_tag.string:
            continue

        # Получаем ID тега script, если есть
        script_id = script_tag.get('id', '')

        # Используем regex для извлечения JSON
        try:
            for j, json_obj in enumerate(extract_json_objects(script_tag.string)):
                json_type = is_json_object_of_interest(json_obj)
                if json_type:
                    # Сохраняем JSON в соответствующую переменную
                    json_objects[json_type] = json_obj
        except:
            continue
    return json_objects


def get_new_size(wix_product, new_product):
    current_choices = set(frozenset({
                                        'color': variant['choices']['Цвет'],
                                        'size': variant['choices']['Размер']
                                    }.items()) for variant in wix_product['product']['variants'] if
                          variant['variant']['visible'])

    new_choices = set(frozenset({
                                    'color': variant['color_name'],
                                    'size': variant['size_name']
                                }.items()) for variant in new_product['price'] if variant['isExist'])

    difference = [dict(i) for i in new_choices - current_choices]
    return difference


def group_by_color(product_variants):
    return [{'color': key, 'items': list(group)} for key, group in
            groupby(product_variants, key=lambda d: d['choices']['Цвет'])]


def get_new_price(last_price, item):
    if last_price > item['min_price_eur']:
        return {'new_price': item['min_price_eur'], 'old_price': last_price}


def get_min_price_eur(prices):
    positive_prices = [item['price_eur'] for item in prices if item['price_eur'] > 0]
    return min(positive_prices) if positive_prices else 0

