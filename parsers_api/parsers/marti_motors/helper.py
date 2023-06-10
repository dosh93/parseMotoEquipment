import re
import copy

from parsers_api.logger import logger
from parsers_api.data.markup import apply_markup
from parsers_api.my_helper.helpers import get_price_rub
from parsers_api.parsers.common_marti_motors.common import get_price_with_promo

from parsers_api.parsers.marti_motors.locators import button_cooke_accept_xpath, id_table_spec, \
    product_descriptions_xpath, \
    link_photo_xpath, child_element_color_xpath, photos_slider_xpath, input_count_xpath, button_add_xpath, colors_xpath, \
    price_xpath, sizes_xpath, promo_checkbox_xpath, id_product_attribute_xpath


async def accept_cookies(browser_handler_instance):
    await browser_handler_instance.wait_for_element(button_cooke_accept_xpath, timeout=10000)
    await browser_handler_instance.click(button_cooke_accept_xpath)


async def get_spec(browser_handler_instance):
    soup = await browser_handler_instance.get_soup()
    rows = soup.find(id=id_table_spec).find_all('tr')
    specification = {}
    for row in rows:
        columns = row.find_all('td')
        if len(columns) == 2:
            key = columns[0].get_text().strip()
            value = columns[1].get_text().strip()
            specification[key] = value
    return specification


async def get_description(spec, browser_handler_instance):
    description_text = await browser_handler_instance.get_element_text(product_descriptions_xpath)
    description_text += "\n"
    if len(spec) > 0:
        description_text += "<ul>"
    for key, value in spec.items():
        description_text += f"<li><strong>{key}</strong> - {value}</li>\n"
    if len(spec) > 0:
        description_text += "</ul>"
    return description_text


async def get_photos_link(browser_handler_instance):
    return await browser_handler_instance.get_attributes_by_xpath(link_photo_xpath, "href")


async def get_color_name(color_element, browser_handler_instance):
    pattern_modelo = r'\bModelo(?:\s+\d+)?\s*'
    pattern_non_alnum = r'^\W'
    child_element = await color_element.xpath(child_element_color_xpath)
    color_name = await browser_handler_instance.get_text_for_element(child_element[0])
    result = re.sub(pattern_modelo, '', color_name)
    result = re.sub(pattern_non_alnum, '', result)
    return result


async def get_count_active_photo(browser_handler_instance):
    swiper_sliders = await browser_handler_instance.get_elements_by_xpath(photos_slider_xpath)
    for index, swiper_slider in enumerate(swiper_sliders):
        name_class = await browser_handler_instance.get_attribute_by_element(swiper_slider, "className")
        if "active" in name_class:
            return index


async def get_count(browser_handler_instance):
    input_count = await browser_handler_instance.get_elements_by_xpath(input_count_xpath)
    start_count = await browser_handler_instance.get_attribute_by_element(input_count[0], "value")

    while True:
        button_add = await browser_handler_instance.get_elements_by_xpath(button_add_xpath)
        await browser_handler_instance.click_for_element(button_add[0])
        input_count = await browser_handler_instance.get_elements_by_xpath(input_count_xpath)
        current_count = await browser_handler_instance.get_attribute_by_element(input_count[0], "value")

        if current_count == start_count:
            return current_count
        start_count = current_count


def map_photo_to_color(data):
    data["photoByColor"] = sorted(data["photoByColor"], key=lambda x: x["count_active_photo"])

    for i, color_data in enumerate(data["photoByColor"]):
        start_index = color_data["count_active_photo"]
        if i < len(data["photoByColor"]) - 1:
            end_index = data["photoByColor"][i + 1]["count_active_photo"]
        else:
            end_index = len(data["photos"])

        color_data["photos"] = data["photos"][start_index:end_index]


def get_all_color(item):
    return set(price["color_name"] for price in item["price"])


def get_all_size(item):
    return sorted(set(price["size_name"] for price in item["price"]))


def get_variants(item):
    variants = []
    colors_choices = []
    sizes_choices = []

    color_by_item = get_all_color(item)
    sizes_by_item = get_all_size(item)
    for color in color_by_item:
        colors_choices.append({
            "value": color,
            "description": color
        })

    for size in sizes_by_item:
        sizes_choices.append({
            "value": size,
            "description": size
        })

    colors = {
        "name": "Цвет",
        "choices": colors_choices
    }
    sizes = {
        "name": "Размер",
        "choices": sizes_choices
    }
    variants.append(colors)
    variants.append(sizes)
    return variants


def get_variant_with_price(item):
    variants = []
    for variant in item['price']:
        choices = {
            "Размер": variant['size_name'],
            "Цвет": variant['color_name']
        }
        if variant['isExist']:
            variants.append({
                "choices": choices,
                "price": variant['price'],
                "sku": variant['sku'],
                "visible": True

            })
        else:
            variants.append({
                "choices": choices,
                "visible": False
            })
    variants_obj = {
        "variants": variants
    }
    return variants_obj


def get_media(item, max_photos=15):
    media_arr = []
    if len(item["photos"]) > max_photos:
        if len(item["photoByColor"]) > max_photos:
            photos = item["photos"][:max_photos]
            for photo in photos:
                media_arr.append({
                    "url": photo
                })
        else:
            count = 0
            copy_photo_by_color = copy.deepcopy(item["photoByColor"])
            while count < max_photos:
                for photos_by_color in copy_photo_by_color:
                    photos = photos_by_color['photos']
                    if len(photos) > 0:
                        media_arr.append({
                            "url": photos[0],
                            "choice": {
                                "option": "Цвет",
                                "choice": photos_by_color["color"]
                            }
                        })
                        del photos[0]
                        count += 1
                        if count == max_photos:
                            break


    else:
        for photoByColor in item["photoByColor"]:
            for photo in photoByColor["photos"]:
                media_arr.append({
                    "url": photo,
                    "choice": {
                        "option": "Цвет",
                        "choice": photoByColor["color"]
                    }
                })
    media = {"media": media_arr}
    return media


async def wait_load_page(browser_handler_instance):
    await browser_handler_instance.wait_for_element(colors_xpath)
    await browser_handler_instance.wait_for_element(sizes_xpath)
    await browser_handler_instance.wait_for_element(price_xpath)


async def is_promo_checked(browser_handler_instance):
    class_name = await browser_handler_instance.get_attribute_by_xpath(promo_checkbox_xpath, "className")
    if class_name == "checked":
        return True
    else:
        return False


async def get_price_on_page(browser_handler_instance, rate, markups, url):
    id_product_attribute = await browser_handler_instance.get_attribute_by_xpath(id_product_attribute_xpath, "value")
    current_price = get_price_with_promo(url, id_product_attribute)
    logger.info(f"Price with promo {current_price}")
    current_price = apply_markup(current_price, markups, url)
    return get_price_rub(current_price, rate)


def form_cookie_string(cookies_dict):
    return '; '.join([f'{k}={v}' for k, v in cookies_dict.items()])
