import asyncio
import configparser
import os

from bs4 import BeautifulSoup
from pyppeteer import launch

from common.logger import configure_logger

logger = configure_logger(__name__)


class BrowserHandler:
    def __init__(self):
        self.browser = None
        self.page = None

        config = configparser.ConfigParser()
        config_file_path = os.path.join(os.path.dirname(__file__), '..', 'config.ini')
        config.read(config_file_path)

        self.browser_args = []
        self.executable_path = None
        if 'browser' in config.sections():
            if 'security_args' in config['browser']:
                security_args = config['browser']['security_args'].split(',')
                self.browser_args.extend(security_args)
            if 'executable_path' in config['browser']:
                self.executable_path = config['browser']['executable_path']

        self.page_load_timeout = config.getint('browser', 'page_load_timeout')
        self.is_headless = config.getboolean('browser', 'is_headless')

    async def start_browser(self):
        try:
            self.browser = await launch(
                args=self.browser_args,
                executablePath=self.executable_path,
                headless=self.is_headless)
            self.page = await self.browser.newPage()
            self.page.setDefaultNavigationTimeout(self.page_load_timeout)
            logger.info("Browser started successfully.")
        except Exception as e:
            logger.error(f"Error starting browser: {e}")
            return False
        return True

    async def navigate_to(self, url, wait_navigate=False):
        if self.page is None:
            logger.error("Browser is not started. Call 'start_browser()' first.")
            return False

        try:
            if wait_navigate:
                await self.page.goto(url)
            else:
                await self.page.goto(url, {'waitUntil': 'domcontentloaded'})

            logger.debug(f"Successfully navigated to {url}.")
        except Exception as e:
            logger.error(f"Error navigating to {url}: {e}")
            return False
        return True

    async def get_page_content(self):
        if self.page is None:
            logger.error("Browser is not started. Call 'start_browser()' first.")
            return None

        try:
            content = await self.page.content()
            logger.debug("Page content retrieved successfully.")
            return content
        except Exception as e:
            logger.error(f"Error getting page content: {e}")
            return None

    async def close_browser(self):
        if self.browser is not None:
            try:
                await self.browser.close()
                logger.info("Browser closed successfully.")
            except Exception as e:
                logger.error(f"Error closing browser: {e}")
                return False
        return True

    async def get_element_text(self, xpath):
        if self.page is None:
            logger.error("Browser is not started. Call 'start_browser()' first.")
            return None

        try:
            elements = await self.page.xpath(xpath)
            if not elements:
                logger.warning(f"No element found for XPath '{xpath}'")
                return None
            element = elements[0]
            text = await self.page.evaluate('(element) => element.textContent', element)
            logger.debug(f"Element text for XPath '{xpath}' retrieved successfully.")
            return text
        except Exception as e:
            logger.error(f"Error getting element text for XPath '{xpath}': {e}")
            return None

    async def get_elements_text(self, xpath):
        if self.page is None:
            logger.error("Browser is not started. Call 'start_browser()' first.")
            return None

        try:
            elements = await self.page.xpath(xpath)
            texts = []
            for element in elements:
                text = await (await element.getProperty('textContent')).jsonValue()
                texts.append(text.strip())
            logger.debug(f"Elements text for XPath '{xpath}' retrieved successfully.")
            return texts
        except Exception as e:
            logger.error(f"Error getting elements text for XPath '{xpath}': {e}")
            return None

    async def type_input(self, xpath, text):
        if self.page is None:
            logger.error("Browser is not started. Call 'start_browser()' first.")
            return False

        try:
            elements = await self.page.xpath(xpath)
            if not elements:
                logger.warning(f"No element found for XPath '{xpath}'")
                return False
            element = elements[0]
            await self.page.evaluate('(element) => element.value = ""', element)  # Очищаем поле перед вводом текста
            await element.type(text)
            logger.debug(f"Text typed into input with XPath '{xpath}' successfully.")
        except Exception as e:
            logger.error(f"Error typing text into input with XPath '{xpath}': {e}")
            return False
        return True

    async def scroll_to_top(self):
        if self.page is None:
            logger.error("Browser is not started. Call 'start_browser()' first.")
            return False

        try:
            await self.page.evaluate('window.scrollTo(0, 0)')
            logger.debug("Scrolled to the top of the page.")
        except Exception as e:
            logger.error(f"Error scrolling to the top of the page: {e}")
            return False
        return True

    async def scroll_to_element(self, element, offset_y=0):
        if self.page is None:
            logger.error("Browser is not started. Call 'start_browser()' first.")
            return False

        try:
            await self.page.evaluate('(element, offsetY) => {element.scrollIntoView(); window.scrollBy(0, offsetY)}',
                                     element, offset_y)
            logger.debug(f"Scrolled to the element with an offset of {offset_y}.")
        except Exception as e:
            logger.error(f"Error scrolling to the element with an offset of {offset_y}: {e}")
            return False
        return True

    async def click(self, xpath, offset_y=-100):
        if self.page is None:
            logger.error("Browser is not started. Call 'start_browser()' first.")
            return False

        try:
            elements = await self.page.xpath(xpath)
            if not elements:
                logger.warning(f"No element found for XPath '{xpath}'")
                return False
            element = elements[0]

            await element.click()
            logger.debug(f"Element with XPath '{xpath}' clicked successfully.")
        except Exception as e:
            logger.error(f"Error clicking element with XPath '{xpath}': {e}")
            return False
        return True

    async def click_for_element(self, element, offset_y=-100):
        if self.page is None:
            logger.error("Browser is not started. Call 'start_browser()' first.")
            return False

        try:
            await element.click()
            logger.debug("Element clicked successfully.")
        except Exception as e:
            logger.error(f"Error clicking element: {e}")
            return False
        return True

    async def wait_for_navigation(self, wait_options=None):
        if self.page is None:
            logger.error("Browser is not started. Call 'start_browser()' first.")
            return False

        if wait_options is None:
            wait_options = {"waitUntil": "load"}

        try:
            await self.page.waitForNavigation(wait_options)
            logger.debug(f"Navigation completed successfully with options {wait_options}.")
        except Exception as e:
            logger.error(f"Error waiting for navigation with options {wait_options}: {e}")
            return False
        return True

    async def get_element_xpath(self, element):
        if self.page is None:
            logger.error("Browser is not started. Call 'start_browser()' first.")
            return None

        try:
            xpath = await self.page.evaluate('''(element) => {
                let xpath = '';
                for (; element && element.nodeType == 1; element = element.parentNode) {
                    let id = Array.from(element.parentNode.children).indexOf(element) + 1;
                    id > 0 ? (id = '[' + id + ']') : (id = '');
                    xpath = '/' + element.tagName.toLowerCase() + id + xpath;
                }
                return '/' + xpath;  // Добавьте '/' перед первым элементом для получения абсолютного XPath
            }''', element)
            logger.debug(f"Absolute XPath for the element retrieved successfully: {xpath}")
            return xpath
        except Exception as e:
            logger.error(f"Error getting absolute XPath for the element: {e}")
            return None

    async def wait_for_element(self, xpath, timeout=None):
        if self.page is None:
            logger.error("Browser is not started. Call 'start_browser()' first.")
            return None

        try:
            timeout = timeout or self.page_load_timeout
            element = await self.page.waitForXPath(xpath, {'visible': True, 'timeout': timeout})
            logger.debug(f"Element with XPath '{xpath}' appeared on the page.")
            return element
        except TimeoutError:
            logger.warning(f"Element with XPath '{xpath}' did not appear within {timeout} ms.")
            return None
        except Exception as e:
            logger.error(f"Error waiting for element with XPath '{xpath}': {e}")
            return None

    async def get_soup(self):
        if self.page is None:
            logger.error("Browser is not started. Call 'start_browser()' first.")
            return None

        try:
            content = await self.page.content()
            soup = BeautifulSoup(content, 'html.parser')
            logger.debug("Successfully converted page content to BeautifulSoup object.")
            return soup
        except Exception as e:
            logger.error(f"Error converting page content to BeautifulSoup object: {e}")
            return None

    async def get_elements_by_xpath(self, xpath):
        if self.page is None:
            logger.error("Browser is not started. Call 'start_browser()' first.")
            return None

        try:
            elements = await self.page.xpath(xpath)
            logger.debug(f"Found {len(elements)} elements with XPath '{xpath}'.")
            return elements
        except Exception as e:
            logger.error(f"Error finding elements with XPath '{xpath}': {e}")
            return None

    async def get_text_for_element(self, element):
        if not element:
            logger.error("Element is None.")
            return None

        try:
            text = await element.getProperty('textContent')
            text = await text.jsonValue()
            text = text.strip()
            logger.debug(f"Found text '{text}' for element.")
            return text
        except Exception as e:
            logger.error(f"Error getting text for element: {e}")
            return None

    async def get_attribute_by_xpath(self, xpath, attribute_name):
        try:
            element = await self.get_elements_by_xpath(xpath)
            if not element:
                logger.error(f"No element found for xpath '{xpath}'")
                return None

            attribute_value = await element[0].getProperty(attribute_name)
            attribute_value = await attribute_value.jsonValue()
            logger.debug(f"Attribute '{attribute_name}' for element '{xpath}' found: {attribute_value}")
            return attribute_value
        except Exception as e:
            logger.error(f"Error getting attribute '{attribute_name}' for element '{xpath}': {e}")
            return None

    async def get_attribute_by_element(self, element, attribute_name):
        try:
            attribute_value = await element.getProperty(attribute_name)
            attribute_value = await attribute_value.jsonValue()
            logger.debug(f"Attribute '{attribute_name}' for element found: {attribute_value}")
            return attribute_value
        except Exception as e:
            logger.error(f"Error getting attribute '{attribute_name}' for element : {e}")
            return None

    async def get_attributes_by_xpath(self, xpath, attribute_name):
        try:
            elements = await self.get_elements_by_xpath(xpath)
            if not elements:
                logger.error(f"No elements found for xpath '{xpath}'")
                return None

            attributes_values = []
            for element in elements:
                attribute_value = await element.getProperty(attribute_name)
                attribute_value = await attribute_value.jsonValue()
                attributes_values.append(attribute_value.strip())

            logger.debug(f"Attribute '{attribute_name}' for elements '{xpath}' found: {attributes_values}")
            return attributes_values
        except Exception as e:
            logger.error(f"Error getting attributes '{attribute_name}' for elements '{xpath}': {e}")
            return None

    async def remove_element_by_xpath(self, xpath):
        try:
            elements = await self.get_elements_by_xpath(xpath)
            await self.page.evaluate('''(element) => element.remove()''', elements[0])

            logger.info(f"Element removed with xpath: {xpath}")
        except Exception as e:
            logger.error(f"Error remove element with xpath {xpath}: {e}")

    async def element_exists_by_xpath(self, xpath):
        elements = await self.page.xpath(xpath)
        if not elements:
            logger.debug(f"Element not found by XPath: {xpath}")
            return False
        logger.debug(f"Element found by XPath: {xpath}")
        return True

    async def is_element_visible_by_xpath(self, xpath):
        elements = await self.page.xpath(xpath)

        if not elements:
            logger.error(f"Element not found by XPath: {xpath}")
            return False

        element = elements[0]
        is_visible = await self.page.evaluate('''(element) => {
            return element.offsetWidth > 0 && element.offsetHeight > 0
        }''', element)

        if is_visible:
            logger.debug(f"Element is visible by XPath: {xpath}")
        else:
            logger.debug(f"Element is not visible by XPath: {xpath}")

        return is_visible
