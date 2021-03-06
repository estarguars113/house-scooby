# -*- coding: utf-8 -*-

from scrapy import Spider, Request
from scrapy.loader import ItemLoader
from scrapper.items import PropertyItem, extract_digits
import re
import sys


class FincaRaizSpider(Spider):
    name = "finca_raiz"
    allowed_domains = ["fincaraiz.com.co"]
    # types = ['apartamento', 'casa-lote', 'casa-campestre', 'casa', 'lote', 'finca']
    types = ['casa', 'lote', 'apartamento']
    cities = ['cali']
    # cities = ['cali', 'jamundi', 'palmira']
    min_price = '0'

    def __init__(self, max_prixe='300000000', **kwargs):
        self.max_price = max_prixe
        super().__init__(**kwargs)

    def start_requests(self):
        base_url = 'https://www.fincaraiz.com.co/{0}/venta/{1}/?ad=30|1||||1||8,23|||82|8200006||{2}|{3}||||||||||||||||1||griddate%20desc||||-1||'
        for t in self.types:
            for c in self.cities:
                yield Request(
                    base_url.format(t, c, self.min_price, self.max_price),
                    self.parse
                )

    def parse(self, response):
        # by default the first one it's advertising, so skip if there's only one remaining
        if len(response.css('ul.advert').extract()) < 2:
            return
        else:
            for item in response.css('ul.advert'):
                property_item = ItemLoader(item=PropertyItem(), response=response)
                # clean input data
                name = item.css('li.title-grid .span-title>a h2.h2-grid::text').extract_first() or \
                    item.css(
                        'li.information .title-grid a::attr(title)').extract_first()
                property_item.add_value('name', name)

                property_type = name.split(' en ')[0]
                property_item.add_value('property_type', property_type)

                price = item.css('li.price div:first-child meta::attr(content)').extract_first() or \
                    item.css(
                        'li.information .title-grid .descriptionPrice::text').extract_first()
                property_item.add_value('price', price)
                
                property_url = response.urljoin(
                    item.css('li.title-grid .span-title>a::attr(href)').extract_first())
                property_item.add_value('link', property_url)
                property_item.add_css('bedrooms', 'li.surface>div::text')
                
                # call single element page
                request = Request(property_url, self.parse_single)
                request.meta['loader'] = property_item
                yield request

            current_url = response.request.url
            next_page_pattern = r"(.*ad=30\|)(\d+)"
            next_page = str(
                int(re.match(next_page_pattern, current_url).group(2)) + 1)

            next_url = re.sub(next_page_pattern, r'\g<1>{next_page}', current_url)
            if next_url is not None:
                next_url = response.urljoin(next_url)
                yield Request(next_url, self.parse)

    def parse_single(self, response):
        item = response.meta['loader']
        item.add_value(
            'internal_id',
            extract_digits(response.css('h2.description>span::text').extract_first())
        )
        item.add_value(
            'status',
            response.css('div.badge_used::text').extract_first()
        )
        item.add_value(
            'publication_date',
            response.css('div.historyAdvert .boxcube ul li::first-child span::text').extract_first()
        )
        item.add_value(
            'bathrooms',
            response.css('div.features>span:nth-child(3)').extract_first()
        )
        item.add_value(
            'parking_spots',
            response.css('div.features>span:nth-child(4)').extract_first()
        )

        neighborhood = response.css('div.breadcrumb.left a:last-of-type::text').extract_first()
        city = response.css('div.breadcrumb.left a:nth-of-type(3)::text').extract_first()

        item.add_value('neighborhood', neighborhood)
        item.add_value('city', city)

        feature_names = response.css('div.features_2 li>b::text').extract()
        feature_values = [fv for fv in response.css(
            'div.features_2 li::text').extract() if fv.strip() != '']
        features_dict = dict(zip(feature_names, feature_values))
        if('Estrato:' in feature_names):
            item.add_value('stratum', features_dict.pop('Estrato:', ''))

        if('Antigüedad:' in feature_names):
            item.add_value('antiquity', features_dict.pop('Antigüedad:', ''))

        if('Área Const.:' in feature_names):
            item.add_value(
                'surface', features_dict.pop('Área Const.:', '').split("a")[-1].replace(",", "."))
        elif('Área privada:' in feature_names):
            item.add_value(
                'surface', features_dict.pop('Área privada:', '').split("a")[-1].replace(",", "."))

        # extract text
        item.add_value('description', response.css(
            '.description p::text').extract_first())

        yield item.load_item()
