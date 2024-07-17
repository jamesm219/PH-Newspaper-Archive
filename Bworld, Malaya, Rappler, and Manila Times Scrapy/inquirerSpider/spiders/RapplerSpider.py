import scrapy


class RapplerspiderSpider(scrapy.Spider):
    name = "RapplerSpider"
    allowed_domains = ["rappler.com"]
    start_urls = ["https://www.rappler.com/"]

    def parse(self, response):
        for link in response.css('h3 a::attr(href)').getall():
            yield response.follow(link, callback=self.parse_content)
        pass

    def parse_content(self, response):
        try:
            author = response.css('div.post-single__authors a.post-single__author::text').getall()
            if not author:
                author = response.css('a.post-single__author::text').get()
                if not author:
                    author = response.css('div.post-single__authors::text').get()
        except:
            author = None
        yield{
            'title': response.css('h1.post-single__title::text').get(),
            'author': author,
            'date': response.css('span.posted-on time.entry-date.published.post__timeago::text').get(),
            'article': response.css('div.post-single__content.entry-content p::text, div.post-single__content.entry-content p a::text').getall(),
            'link': response.css('meta[property="og:url"]::attr(content)').get()

        }