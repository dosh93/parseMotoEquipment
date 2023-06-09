import json
import uuid
from asyncio import sleep

from parsers_api.parsers.browser_handler import BrowserHandler
from parsers_api.parsers.marti_motors.helper import accept_cookies, get_description, get_photos_link, get_color_name, \
    get_spec, \
    get_count_active_photo, map_photo_to_color, wait_load_page, is_promo_checked, get_price_on_page
from parsers_api.parsers.marti_motors.locators import colors_xpath, name_xpath, sizes_xpath, input_size_xpath, id_price, \
    id_sku, \
    class_sku, header_xpath, promo_xpath, price_xpath, cooke_accept_banner_xpath

from parsers_api.logger import logger


async def parse_by_url(url, rate, markups):
    browser_handler_instance = None
    try:
        browser_handler_instance = BrowserHandler()
        logger.info(f"Start parse by url {url}")
        await browser_handler_instance.start_browser()
        result = await browser_handler_instance.navigate_to(url)
        if not result:
            raise Exception("Not navigate")
        await wait_load_page(browser_handler_instance)
        await browser_handler_instance.remove_element_by_xpath(header_xpath)
        soup = await browser_handler_instance.get_soup()
        item = {"name": await browser_handler_instance.get_element_text(name_xpath), "base_url": url,
                "specification": await get_spec(browser_handler_instance), "price": [],
                "photos": await get_photos_link(browser_handler_instance), "photoByColor": []}
        item["description"] = await get_description(item["specification"], browser_handler_instance)

        colors = await browser_handler_instance.get_elements_by_xpath(colors_xpath)

        for color in colors:
            if await browser_handler_instance.element_exists_by_xpath(cooke_accept_banner_xpath):
                await browser_handler_instance.remove_element_by_xpath(cooke_accept_banner_xpath)

            color_name = await get_color_name(color, browser_handler_instance)
            logger.info(f"Parse color {color_name}")
            await browser_handler_instance.click_for_element(color)
            item["photoByColor"].append({"color": color_name,
                                         "count_active_photo": await get_count_active_photo(browser_handler_instance)})

            size_elements = await browser_handler_instance.get_elements_by_xpath(sizes_xpath)
            for size in size_elements:
                price = {}
                input_size = await size.xpath(input_size_xpath)
                if await browser_handler_instance.get_attribute_by_element(input_size[0], "disabled"):
                    price['price'] = "0"
                    price['isExist'] = False
                else:
                    await browser_handler_instance.click_for_element(size)

                    price['price'] = await get_price_on_page(browser_handler_instance, rate, markups, url)
                    price['isExist'] = True
                    soup = await browser_handler_instance.get_soup()
                    price['sku'] = soup.find(id=id_sku).find(class_=class_sku).get_text().strip()

                size_name = await browser_handler_instance.get_text_for_element(size)
                price['color_name'] = color_name
                price['size_name'] = size_name.strip()
                item["price"].append(price)

        item["one_price"] = await get_price_on_page(browser_handler_instance, rate, markups, url)
        map_photo_to_color(item)
        logger.info(f"Done parse {url}")
        logger.debug(f"json: \n{json.dumps(item, indent=2)}")
        return item
    except Exception as e:
        logger.error(f"Error parsing {e}")
    finally:
        if browser_handler_instance is not None:
            await browser_handler_instance.close_browser()

