# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
from scrapy.http import HtmlResponse
import re
import tesserocr
from PIL import Image


class UserAgentMiddleware(object):
    def __init__(self):
        self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"

    def process_request(self, request, spider):
        request.headers['User-Agent'] = self.user_agent


class SeleniumMiddleware(object):
    def __init__(self, timeout=None):
        self.timeout = timeout
        self.chrome_options = webdriver.ChromeOptions()
        #self.chrome_options.add_argument('--proxy-server=http://127.0.0.1:1087')
        self.chrome_options.add_argument('--kiosk')
        self.browser = webdriver.Chrome(chrome_options=self.chrome_options)
        self.wait = WebDriverWait(self.browser, self.timeout)
        self.browser.get('https://m.dianping.com/awp/h5/hotel-dp/list/list.html?cityid=143&from=m_nav_3_jiudian')
        self.pattern = 'verify'

    def __del__(self):
        self.browser.close()

    def process_request(self, request, spider):
        js = request.meta.get('js')
        if js:
            if js != "var q=document.documentElement.scrollTop=0":
                self.browser.execute_script(js)
                time.sleep(0.9)

        js_detail = request.meta.get('js_detail')
        if js_detail:
            self.browser.get(request.url)
            if re.search(self.pattern, self.browser.current_url):
                self.recognize_verify_code(self.browser.current_url)
            time.sleep(20)
            btn = self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, '#main > div > div.shop-brief > a > div.click_area_new > div > span')))
            btn.click()
            self.browser.get(request.url)
            time.sleep(20)

        try:
            return HtmlResponse(url=request.url, body=self.browser.page_source, request=request, encoding='utf-8',
                                status=200)
        except TimeoutException:
            return HtmlResponse(url=request.url, status=500, request=request)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(timeout=crawler.settings.get('SELENIUM_TIMEOUT'))

    def recognize_verify_code(self, url):
        self.browser.get(url)
        self.browser.save_screenshot('./verify.jpg')
        imgElement = self.browser.find_element_by_class_name('_image__image___2zgEG')
        left = imgElement.location['x']
        top = imgElement.location['y']
        elementWidth = imgElement.location['x'] + imgElement.size['width']
        elementHeight = imgElement.location['y'] + imgElement.size['height']
        image = Image.open('./verify.jpg')
        image = image.crop((left, top, elementWidth, elementHeight))
        image = image.convert('L')
        threshold = 127
        table = []
        for i in range(256):
            if i < threshold:
                table.append[0]
            else:
                table.append(1)
        image = image.point(table, '1')
        result = tesserocr.image_to_text(image)
        input = self.browser.find_element_by_class_name('_image__imageInput___2SPQH')
        input.clear()
        time.sleep(1)
        time.send_keys(result)
        time.sleep(1.5)
        verify = self.browser.find_element_by_class_name('_image__sure___2RS04')
        verify.click()