import time

import scrapy
from scrapy_selenium import SeleniumRequest
from scrapy.selector import Selector
from loguru import logger
from selenium.webdriver.support.ui import WebDriverWait



class ScrapeSpider(scrapy.Spider):
    name = 'scrape'
    allowed_domains = ['www.olx.ua']

    def start_requests(self):
        yield scrapy.Request(url='https://www.olx.ua/list/q-mac-book-pro-2015/', callback=self.parse_pages)

    def parse_pages(self, response):
        products = response.xpath("//div[@class='space rel']/h3/a")
        for product in products:

            self.link = product.xpath(".//@href").get()
            logger.info(f"go to page{self.link}")
            yield SeleniumRequest(
                url=self.link,
                callback=self.parse_link,
                wait_time=3,

            )
        next_page = response.xpath("//a[@data-cy='page-link-next']/@href").get()
        if next_page:
            yield scrapy.Request(url=next_page, callback=self.parse_pages)

    def parse_link(self, response):
        logger.info(f'Start parse page{self.link}')
        driver = response.meta['driver']
        items = response.xpath("//div[@class='css-14c9e9']")

        olx_delyvery = response.xpath("//div[@class='css-x30oa2-Text eu5v0x0']/text()").get()
        if olx_delyvery:
            olx_delyvery = 'True'
        else:
            olx_delyvery = 'False'

        try:
            upper_info_box =  WebDriverWait(driver, 4).until(lambda d: d.find_element_by_xpath("//div[@data-cy='seller_card']"))
            driver.execute_script("arguments[0].scrollIntoView();", upper_info_box)
            time.sleep(1)
            phone_button = WebDriverWait(driver, 4).until(lambda d: d.find_element_by_xpath("//button[@data-cy='ad-contact-phone']"))
            phone_button.click()
            time.sleep(1)
            new_html = driver.page_source
            response = Selector(text=new_html)
            phone = response.xpath("//button[@data-cy='ad-contact-phone']/text()").get()
            logger.warning(f'phone==={phone}')
        except:
            phone = 'not_found'
            logger.warning(f"not found phone_button")


        condition = []
        for item in items.xpath(".//ul/li"):
            condition.append(item.xpath(".//p/text()").get())

        if 'Состояние: Б/у' in condition:
            condition = 'was in use'
        elif 'Состояние: Новый' in condition:
            condition = 'new'

        seller_name = response.xpath("(//h2[@class='css-owpmn2-Text eu5v0x0'])[1]/text()").get()
        seller_on_olx = response.xpath("(//div[@class='css-1bafgv4-Text eu5v0x0'])[1]/text()").get().split('на OLX с ')[1]
        seller_last_online = response.xpath("(//div[@class='css-1dqk056-Text'])[1]/div/div/text()").get().split('Онлайн в ')[1]
        try:
            upper_info_box = driver.find_element_by_xpath("//div[@class='css-cgp8kk']")
            driver.execute_script("arguments[0].scrollIntoView();", upper_info_box)
            new_html = driver.page_source
            response = Selector(text=new_html)
            views = response.xpath("//span[@data-testid='page-view-text']/text()").get().split(':')[1]

        except:
            logger.warning('views not found')
            views = 'none'
        yield {
            "name": items.xpath(".//div[@class='css-sg1fy9']/h1/text()").get(),
            "price": items.xpath(".//div[@class='css-dcwlyx']/h3/text()").get(),
            "condition": condition,
            "olx delivery": olx_delyvery,
            "views": views,
            "seller name": seller_name,
            "seller on olx": seller_on_olx,
            "seller last online": seller_last_online,
            "seller phone": phone,
            "url": driver.current_url,
        }

