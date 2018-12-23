# -*- coding: utf-8 -*-

from scrapy import Spider, Request
from scrapy.loader import ItemLoader
import re

# custom item definition
from scrapper.items import PropertyItem

ZONES = ['cali-y-region-sur-occidente']
CITIES = ['cali', 'jamundi']
TYPES = ['casas', 'lotes', 'apartamentos']


class vivendoSpider(Spider):
    name = "vivendo"
    allowed_domains = ["vivendo.co"]

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
            property_item.add_css('responsible', 'div.address::text')
            property_item.add_css('bathrooms', '.views-field-field-banos>div::text')
            bedrooms = response.css('.views-field-field-alcobas>div::text').extract_first()
            if(isinstance(bedrooms, str) and 'o' in bedrooms):
                bedrooms = bedrooms.split('o')[-1].split()
            property_item.add_value('bedrooms', bedrooms)

            # call single element page
            request = Request(property_url, self.parse_single)
            request.meta['loader'] = property_item
            yield request

    def parse_single(self, response):
        item = response.meta['loader']

        # to-do internal unique identifier
        general_type = response.css('#encabezado-izquierdo-texto .field-type-ds .field-item::text').extract_first()
        property_type = re.match(r"(.*)( en)", general_type).group(1)[:-1]

        # specific features
        description = response.css('div.field-name-descripcion-custom  .field-item::text').extract_first()
        item.add_value('description', description)
        item.add_value('name', response.css('h2.titulo_proyecto::text').extract_first())
        item.add_value('surface', response.css('div.field-name-field-area-privada .field-item::text').extract_first())
        item.add_value('price', response.css('div.field-name-field-precio div.field-items>div::text').extract_first())
        item.add_value('city', response.css('#region-area-estado .field-name-field-ciudad .field-item::text').extract_first())
        item.add_value('status', response.css('#region-area-estado .field-name-field-estados .field-item::text').extract_first())
        item.add_value('property_type', property_type)

        # extract features from string
        pattern = r"(.*estrato )(\d+)"
        if 'estrato' in description:
            if(re.match(pattern, description)):
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
