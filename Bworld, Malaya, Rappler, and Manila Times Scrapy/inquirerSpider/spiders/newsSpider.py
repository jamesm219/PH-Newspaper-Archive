import scrapy
import random
from scrapy_selenium import SeleniumRequest

class NewsspiderSpider(scrapy.Spider):
    name = "newsSpider"
    allowed_domains = ["inquirer.net"]
    start_urls = ["https:inquirer.net/"]

    # user_agent_list = [
    #     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246',
    #     'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
    #     'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9',
    #     'Mozilla/5.0 (Linux; Android 12; SM-X906C Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/80.0.3987.119 Mobile Safari/537.36'
    # ]

    # def start_requests(self):
    #     headers = {
    #         'Referer': 'https://www.google.com',
    #         'User-Agent': self.user_agent_list[random.randint(0, len(self.user_agent_list)-1)]
    #     }
    #     for url in self.start_urls:
    #         yield scrapy.Request(url, headers=headers)


    # def parse(self, response):
    #     for link in response.css('div#ncg-info h1 a::attr(href)').getall():
    #         yield response.follow(link, callback=self.parse_content, headers = {"User-Agent": self.user_agent_list[random.randint(0, len(self.user_agent_list)-1)]})

    def parse(self, response):
        for link in response.css('div#ncg-info h1 a::attr(href)').getall():
            yield response.follow(link, callback=self.parse_content)
        
    def parse_content(self, response):
        
        box = response.css('div#article_content.article_align')
        article_body = box.css('p:not(.wp-caption-text):not(.headertext):not(.footertext)::text').getall()
        article_body += box.css('span:not(.wp-caption-text):not(.headertext):not(.footertext):not(.sib-form-message-panel__inner-text)::text').getall()
        yield {
            'title': response.css('h1.entry-title::text').get(),
            'author': response.css('div#art_author a::text').get(),
            'date': response.css('div#art_plat::text').getall(),
            'article': article_body,
            'link': response.css('meta[property="og:url"]::attr(content)').get()
        }
