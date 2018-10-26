# -*- coding: utf-8 -*-

from scrapy import Spider, Request
import re
from scrapper.items import PropertyItem


class vivendoSpider(Spider):
    name = "vivendo"
    allowd_domains = ["vivendo.co"]

    zones = ['cali-y-region-sur-occidente']
    cities = ['cali', 'jamundi']
    options = ̈́['casas', 'lotes', 'apartamentos']

    def start_requests(self):
        base_url = 'https://www.vivendo.co/resultados/{0}/{1}/zona-general/{2}/precio-general/'
        for z in self.zones:
            for c in self.cities:
                for t in self.options:
                    yield Request(
                        base_url.format(z, t, c),
                        self.parse
                    )

    def parse(self, response):
        for item in response.css('div.view-lista-proyectos div.views-row'):
            property_items = PropertyItem()
            property_url = response.urljoin(item.css('div.views-field-title a::attr(href)').extract_first())

            property_item['link'] = property_url
            property_item['name'] = item.css('div.views-field-title a::text').extract_first()
            property_item['responsible'] = item.css('div.views-field-field-constructora').extract_first()
            property_item['price'] = item.css('.image .priceCap span::text').extract_first()
            property_item['bathrooms'] = item.css('.views-field-field-banos>div::text').extract_first()
            property_item['bedrooms'] = item.css('.views-field-field-alcobas>div::text').extract_first()

            # call single element page
            request = Request(property_url, self.parse_single)
            request.meta['item'] = property_item
            yield request

    def parse_single(self, response):
        item = response.meta['item']

        # to-do internal unique identifier

        # specific features
        item['description'] = item.css('div.field-name-descripcion-custom  .field-item::text').extract()
        item['surface'] = item.css('div.group-descripcion .field-items p.rtejustify:first-child()::text').extract_first()
        item['location'] = item.css('#encabezado-izquierdo-texto .field-name-field-direccion .field-item::text').extract_first()
            