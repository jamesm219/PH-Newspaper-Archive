import scrapy
from bs4 import BeautifulSoup


class BworldspiderSpider(scrapy.Spider):
    name = "BWorldSpider"
    allowed_domains = ["bworldonline.com"]
    start_urls = ["https://www.bworldonline.com/top-stories/"]

    def parse(self, response):
        links = response.css('h3 a::attr(href)').getall() + response.css('aside.td_block_template_1.widget.widget_recent_entries a::attr(href)').getall()
        for link in links:
            yield response.follow(link, callback=self.parse_content)
    
    def parse_content(self, response):
        soup = BeautifulSoup(response.text, "lxml")
        try:
            paragraphs = soup.select('div.td-post-content.td-pb-padding-side p')
            if not paragraphs:
                paragraphs = response.css('div.td-post-content.td-pb-padding-side div::text').getall()
        except:
            paragraphs = None
        article_text = ' '.join([paragraph.get_text(strip=True) for paragraph in paragraphs])
        try:
            author = response.css('p.p2 b::text').getall()
            if not author:
                author = response.css('p.p3 b::text').getall()
                if not author:
                    author = response.css('p strong::text').getall()
                    if not author:
                        author = response.css('p.p4 b::text').getall()
                        if not author:
                            author = response.css('p.p1 span.s1 b::text').getall()[2]
                            if not author:
                                author = response.css('p.p1 span.s1 b::text').getall()
        except:
            author = None
        yield{
            'title': response.css('h1.entry-title::text').get(),
            'author': author,
            'date': response.css('span.td-post-date time.entry-date.updated.td-module-date::text').get(),
            'article': article_text,
            'link': response.css('link[rel="canonical"]::attr(href)').get()
        }
        pass
