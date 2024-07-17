import scrapy
import random


class MalayaspiderSpider(scrapy.Spider):
    name = "MalayaSpider"
    allowed_domains = ["malaya.com.ph"]
    start_urls = ["https://malaya.com.ph/news/"]

    user_agent_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246',
        'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9',
        'Mozilla/5.0 (Linux; Android 12; SM-X906C Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/80.0.3987.119 Mobile Safari/537.36'
    ]

    def parse(self, response):
        for link in response.css('h3 a::attr(href)').getall():
            yield response.follow(link, callback=self.parse_content, headers={"User-Agent": self.user_agent_list[random.randint(0, len(self.user_agent_list)-1)]})
    
    def parse_content(self, response):
        box = response.css('div.td-pb-span8.td-main-content')
        try:
            paragraph = box.css('div.td-post-content.tagdiv-type p::text').getall()
            if not paragraph:
                paragraph = box.css('div.td-post-content.tagdiv-type p span::text').getall()
        
        except:
            paragraph = None

        yield{
            'title': box.css('h1.entry-title::text').get(),
            'author': box.css('div.td-post-author-name a::text').getall(),
            'date': box.css('span.td-post-date time::text').getall(),
            'article': paragraph,
            'link': response.css('link[rel="canonical"]::attr(href)').getall()

        }

        pass
