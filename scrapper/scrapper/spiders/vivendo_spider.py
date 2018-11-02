# -*- coding: utf-8 -*-

from scrapy import Spider, Request
from scrapy.loader import ItemLoader
import re
from scrapper.items import PropertyItem

ZONES = ['cali-y-region-sur-occidente']
CITIES = ['cali', 'jamundi']
TYPES = ['casas', 'lotes', 'apartamentos']


class vivendoSpider(Spider):
    name = "vivendo"
    allowd_domains = ["vivendo.co"]

    def start_requests(self):
        base_url = 'https://www.vivendo.co/resultados/{0}/{1}/zona-general/{2}/precio-general/'
        for z in ZONES:
            for c in CITIES:
                for t in TYPES:
                    yield Request(
                        base_url.format(z, c, t),
                        self.parse
                    )

    def parse(self, response):
        for item in response.css('div.view-lista-proyectos div.views-row'):
            property_item = ItemLoader(item=PropertyItem(), response=response)
            property_url = response.urljoin(item.css('div.views-field-title a::attr(href)').extract_first())

            property_item.add_value('link', property_url)
            property_item.add_css('name', 'div.views-field-title a::text')
            property_item.add_css('responsible', 'div.views-field-field-constructora a::text')
            property_item.add_css('price', '.image .priceCap span::text')
            property_item.add_css('bathrooms', '.views-field-field-banos>div::text')
            property_item.add_css('bedrooms', '.views-field-field-alcobas>div::text')

            # call single element page
            request = Request(property_url, self.parse_single)
            request.meta['loader'] = property_item
            yield request

    def parse_single(self, response):
        item = response.meta['loader']

        # to-do internal unique identifier

        # specific features
        description = response.css('div.field-name-descripcion-custom  .field-item::text').extract_first()
        item.add_value('description', description)
        item.add_css('surface','div.field-name-field-area-privada .field-item::text')
        item.add_css('city','#region-area-estado .field-name-field-ciudad .field-item::text')
        item.add_css('status','#region-area-estado .field-name-field-estados .field-item::text')

        # extract features from string
        pattern = r"(.*estrato )(\d+)"
        if 'estrato' in description:
            value = re.match(pattern, description).group(2)
            if value:
                item.add_value('stratum', value)
       
        if('ubicado en' in description or 'sector' in description):
            location = re.match('(.*ubicado en|sector )([\S ]*)[.,]', description).group(2) or \
                        response.css('#encabezado-izquierdo-texto .field-name-field-direccion .field-item::text').extract_first()
            item.add_value('location', location)

        # extract feature list
        item.add_value('features',  list(map(lambda x: x.strip(), response.css('.field-name-field-interiores .field-item::text').extract())))
        
        yield item.load_item()
