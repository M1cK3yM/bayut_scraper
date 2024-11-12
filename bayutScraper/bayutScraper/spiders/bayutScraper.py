import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class BayutScraper(scrapy.Spider):
    name = 'bayutScraper'
    start_urls = [
        'https://www.bayut.com/companies/alkhana-real-estate-104744/']

    def __init__(self, *args, **kwargs):
        super(BayutScraper, self).__init__(*args, **kwargs)
        self.driver = webdriver.Chrome()

    def parse(self, response):
        for listings in response.css('article.fbc619bc._058bd30f'):
            listing_url = response.urljoin(
                listings.css("a.d40f2294::attr(href)").get())
            yield response.follow(listing_url, callback=self.parse_listing)

        current_page = response.url.split("=")[-1]
        if not current_page.isdigit():
            current_page = 1
        else:
            current_page = int(current_page)

        page_numbers = response.css(
            'div[role="navigation"] div[title^="Page"]::attr(title)').re(r'Page (\d+)')
        max_page = max(map(int, page_numbers)) if page_numbers else None

        if max_page is not None and int(current_page) < max_page:
            next_page = f"https://www.bayut.com/companies/alkhana-real-estate-104744/?page={
                int(current_page) + 1}"
            yield response.follow(next_page, callback=self.parse)

    def parse_listing(self, response):
        self.driver.get(response.url)
        time.sleep(7)

        try:
            # Wait until the "View gallery" button is clickable
            view_gallery_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "div[aria-label='View gallery']"))
            )
            view_gallery_button.click()

            # Wait for the gallery container to be present
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "_661933fd"))
            )

            # Extract images from the gallery
            container = self.driver.find_element(
                By.CSS_SELECTOR, "_661933fd")
            images = container.find_elements(By.TAG_NAME, "img")
            image_links = [img.get_attribute('src') for img in images]

            yield {
                'image_urls': image_links,
                'listing_url': response.url  # Include the listing URL for reference
            }
        except Exception as e:
            self.logger.error(f"Error getting images: {e}")
