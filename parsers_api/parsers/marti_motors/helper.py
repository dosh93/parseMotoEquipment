import re
from parsers_api.parsers.marti_motors.singleton import browser_handler

from parsers_api.parsers.marti_motors.locators import button_cooke_accept_xpath, id_table_spec, product_descriptions_xpath, \
    link_photo_xpath, child_element_color_xpath, photos_slider_xpath, input_count_xpath, button_add_xpath


async def accept_cookies():
    await browser_handler().wait_for_element(button_cooke_accept_xpath, timeout=10000)
    await browser_handler().click(button_cooke_accept_xpath)


async def get_spec():
    soup = await browser_handler().get_soup()
    rows = soup.find(id=id_table_spec).find_all('tr')
    specification = {}
    for row in rows:
        columns = row.find_all('td')
        if len(columns) == 2:
            key = columns[0].get_text().strip()
            value = columns[1].get_text().strip()
            specification[key] = value
    return specification


async def get_description():
    return await browser_handler().get_element_text(product_descriptions_xpath)


async def get_photos_link():
    return await browser_handler().get_attributes_by_xpath(link_photo_xpath, "href")


async def get_color_name(color_element):
    pattern = r'\bModelo(?:\s+\d+)?\s*'
    child_element = await color_element.xpath(child_element_color_xpath)
    color_name = await browser_handler().get_text_for_element(child_element[0])
    result = re.sub(pattern, '', color_name)
    return result


async def get_count_active_photo():
    swiper_sliders = await browser_handler().get_elements_by_xpath(photos_slider_xpath)
    for index, swiper_slider in enumerate(swiper_sliders):
        name_class = await browser_handler().get_attribute_by_element(swiper_slider, "className")
        if "active" in name_class:
            return index


async def get_count():
    input_count = await browser_handler().get_elements_by_xpath(input_count_xpath)
    start_count = await browser_handler().get_attribute_by_element(input_count[0], "value")

    while True:
        button_add = await browser_handler().get_elements_by_xpath(button_add_xpath)
        await browser_handler().click_for_element(button_add[0])
        input_count = await browser_handler().get_elements_by_xpath(input_count_xpath)
        current_count = await browser_handler().get_attribute_by_element(input_count[0], "value")

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


def get_media(item):
    media_arr = []
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
