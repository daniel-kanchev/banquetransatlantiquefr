import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from banquetransatlantique.items import Article


class BanquetransatlantiqueSpider(scrapy.Spider):
    name = 'banquetransatlantique'
    start_urls = ['https://www.banquetransatlantique.com/fr/actualites.html']

    def parse(self, response):
        links = response.xpath('//a[@class="more"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_pages = response.xpath('//nav[@class="pagination"]/ul/li/a/@href').getall()
        yield from response.follow_all(next_pages, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//time/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@itemprop="articleBody"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
