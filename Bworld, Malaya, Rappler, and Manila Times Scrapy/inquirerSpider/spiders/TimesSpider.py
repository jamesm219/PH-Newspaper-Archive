import scrapy
import re


class TimesspiderSpider(scrapy.Spider):
    name = "TimesSpider"
    allowed_domains = ["manilatimes.net"]
    start_urls = ["https://www.manilatimes.net/news"]

    def parse(self, response):
        box = response.css('div.col-md-9.col-xs-12')
        links = box.css('a::attr(href)').getall()
        date_pattern = re.compile(r'https:\/\/www\.manilatimes\.net\/\d\d\d\d')

        filtered_hrefs = list(
            set(
                href
                for href in links
                if href is not None and date_pattern.search(href)
            )
        )
        for link in filtered_hrefs:
            yield response.follow(link, callback=self.parse_content)
    
    def parse_content(self, response):
        try:
            paragraph = response.css('p::text').getall()
            if not paragraph or all(text.strip() == '' for text in paragraph):
                paragraph = response.css('div.article-body-content span::text').getall()
        except:
            paragraph = None
        author = response.css('a.article-author-name.roboto-a::text').getall()
        author2 = response.css('a.article-author-name.roboto-a span::text').getall()
        combined_authors = author + author2
        yield{
            'title': response.css('h1.article-title.font-700.roboto-slab-3.tdb-title-text::text').get(),
            'author': combined_authors,
            'date': response.css('div.article-publish-time.roboto-a::text').get(),
            'article': paragraph,
            'link': response.css('meta[property="og:url"]::attr(content)').get()
        }

        pass
