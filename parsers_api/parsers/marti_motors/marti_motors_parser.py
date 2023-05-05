import json

from parsers_api.logger import configure_logger
from parsers_api.my_helper.helpers import get_price_rub
from parsers_api.parsers.marti_motors.singleton import browser_handler
from parsers_api.parsers.marti_motors.helper import accept_cookies, get_description, get_photos_link, get_color_name, get_spec, \
    get_count_active_photo, map_photo_to_color
from parsers_api.parsers.marti_motors.locators import colors_xpath, name_xpath, sizes_xpath, input_size_xpath, id_price, id_sku, \
    class_sku

logger = configure_logger(__name__)


async def parse_by_url(url):
    logger.info(f"Start parse by url {url}")
    await browser_handler().start_browser()
    await browser_handler().navigate_to(url)
    await accept_cookies()
    soup = await browser_handler().get_soup()
    current_price = float(soup.find(id=id_price).get_text().replace(" \u20ac", "").replace(",", ".").strip())
    item = {"name": await browser_handler().get_element_text(name_xpath), "base_url": url,
            "specification": await get_spec(),
            "description": await get_description(), "price": [], "photos": await get_photos_link(), "photoByColor": [],
            "one_price": get_price_rub(current_price, "EUR")}

    colors = await browser_handler().get_elements_by_xpath(colors_xpath)

    for color in colors:
        color_name = await get_color_name(color)
        logger.info(f"Parse color {color_name}")
        await browser_handler().click_for_element(color)
        item["photoByColor"].append({"color": color_name, "count_active_photo": await get_count_active_photo()})

        size_elements = await browser_handler().get_elements_by_xpath(sizes_xpath)
        for size in size_elements:
            price = {}
            input_size = await size.xpath(input_size_xpath)
            if await browser_handler().get_attribute_by_element(input_size[0], "disabled"):
                price['price'] = "0"
                price['isExist'] = False
            else:
                await browser_handler().click_for_element(size)
                soup = await browser_handler().get_soup()
                current_price = float(soup.find(id=id_price).get_text().replace(" \u20ac", "").replace(",", ".").strip())
                price['price'] = get_price_rub(current_price, "EUR")
                price['isExist'] = True
                #price['count'] = await get_count()
                price['sku'] = soup.find(id=id_sku).find(class_=class_sku).get_text().strip()

            size_name = await browser_handler().get_text_for_element(size)
            price['color_name'] = color_name
            price['size_name'] = size_name.strip()
            item["price"].append(price)

    map_photo_to_color(item)
    logger.info(f"Done parse {url}\n{json.dumps(item, indent=2)}")
    await browser_handler().close_browser()
    return item
