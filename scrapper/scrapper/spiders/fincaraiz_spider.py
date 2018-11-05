# -*- coding: utf-8 -*-

from scrapy import Spider, Request
from scrapy.loader import ItemLoader
from scrapper.items import PropertyItem
import re
import sys


class FincaRaizSpider(Spider):
    name = "finca_raiz"
    allowed_domains = ["fincaraiz.com.co"]
    # types = ['apartamento', 'casa-lote', 'casa-campestre', 'casa', 'lote', 'finca']
    types = ['casa']
    cities = ['cali']
    # cities = ['cali', 'jamundi', 'palmira']
    min_price = '0'

    def __init__(self, max_prixe='10000000', **kwargs):
        self.max_price = max_prixe
        super().__init__(**kwargs)
   
    def start_requests(self):
        base_url = 'https://www.fincaraiz.com.co/{0}/venta/{1}/?ad=30|1||||1||8,21,23,7|||82|8200006|8200104|{2}|{3}||||||||||||||||1||griddate%20desc||||-1||'
        for t in self.types:
            for c in self.cities:
                yield Request(
                    base_url.format(t, c, self.min_price, self.max_price),
                    self.parse
                )
         
    def parse(self, response):
        for item in response.css('ul.advert'):
            property_item = ItemLoader(item=PropertyItem(), response=response)
            # clean input data
            description = item.css('li.title-grid .span-title>a h2.h2-grid::text').extract_first() or \
                item.css('li.information .title-grid a::attr(title)').extract_first()
            property_item.add_value('description', description)

            surface = item.css('li.surface::text').extract_first() or \
                item.css('li.information .title-grid .description::text').extract_first()
            property_item.add_value('surface', surface)

            price = item.css('li.price div:first-child meta::attr(content)').extract_first() or \
                item.css('li.information .title-grid .descriptionPrice::text').extract_first()
            property_item.add_value('price', price)

            full_location = item.css('li.title-grid .span-title>a>div:last-child::text').extract_first()
            neighborhood, city = full_location.split('-') if full_location else ["", ""]

            property_url = response.urljoin(item.css('li.title-grid .span-title>a::attr(href)').extract_first())
            property_item.add_value('link', property_url)
            property_item.add_css('bedrooms', 'li.surface>div::text')
            property_item.add_value('neighborhood', neighborhood)
            property_item.add_value('city', city)

            # call single element page
            request = Request(property_url, self.parse_single)
            request.meta['loader'] = property_item
            yield request

        current_url = response.request.url
        next_page_pattern = r"(.*ad=30\|)(\d+)"
        next_page = str(
            int(re.match(next_page_pattern, current_url).group(2)) + 1)

        next_url = re.sub(next_page_pattern, fr'\g<1>{next_page}', current_url)
        if next_url is not None:
            next_url = response.urljoin(next_url)
            yield Request(next_url, self.parse)

    def parse_single(self, response):
        item = response.meta['loader']

        item.add_css('internal_id', 'h2.description>span::text')
        item.add_css('status', 'div.badge_used::text')

        features = '-'.join(response.css('div.features_2 li::text').extract())
        if('Estrato' in features):
            pattern = r"(.*Estrato:|)(\d+)[-]"
            item.add_value('stratum', int(re.match(pattern, features).group(2)))

        if('Antigüedad' in features):
            pattern = r"(.*Antigüedad:|)(\d+)[-]"
            item.add_value('antiquity', int(re.match(pattern, features).group(2)))

        if('Piso' in features):
            pattern = r"(.*Piso No::|)(\d+)[-]"
            item.add_value('floor_location', int(re.match(pattern, features).group(2)))

        # extract text 
        item.add_css('description','.description p::text')

        yield item.load_item()