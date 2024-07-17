import scrapy
from scrapy_selenium import SeleniumRequest

class NewsspiderSpider(scrapy.Spider):
    name = "newsSpider"

    def start_requests(self):
        url = 'https://newsinfo.inquirer.net/'
        yield SeleniumRequest(url=url, wait_time=10, callback=self.parse)


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
