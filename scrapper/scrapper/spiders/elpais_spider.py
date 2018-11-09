# -*- coding: utf-8 -*-

from scrapy import Spider, Request
from scrapy.loader import ItemLoader
import re

# custom item definition
from scrapper.items import PropertyItem


class ElPaisSpider(Spider):
    name = "el_pais"
    allowed_domains = ["fincaraiz.elpais.com.co"]
    # CITIES = ['cali', 'jamundi', 'palmira']
    CITIES = ['cali']
    # TYPES = ['casas', 'lotes', 'apartamentos', 'fincas-y-casas-campestres', 'apartaestudios']
    TYPES = ['casas']

    def start_requests(self):
        base_url = "https://fincaraiz.elpais.com.co/avisos/venta/{0}/{1}"
        for t in self.TYPES:
            for c in self.CITIES:
                yield Request(base_url.format(t, c), self.parse)

    def parse(self, response):
        for item in response.css('article.flexArticle'):
            property_item = ItemLoader(item=PropertyItem(), response=response, selector=item)
            full_description = item.css('div.info div.description::text').extract_first()
            city, rooms, bathrooms, surface = full_description.split(', ') if full_description else ['', 0, 0, 0]
            property_url = response.urljoin(item.css('div.info>a.link-info::attr(href)').extract_first())
            
            # fill properties
            property_item.add_value('link', property_url)
            property_item.add_css('price', 'div.info div.price::text')
            property_item.add_value('bedrooms', rooms)
            property_item.add_value('bathrooms', bathrooms)
            property_item.add_value('city', city)
            property_item.add_value('surface', surface)

            # call single element page
            request = Request(property_url, self.parse_single)
            request.meta['loader'] = property_item
            yield request

        next_page = response.css('nav.pagination-box>ul.pagination>li.next>a::attr(href)').extract_first()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield Request(next_page, callback=self.parse)

    def parse_single(self, response):
        item = response.meta['loader']

        # internal unique identifier
        internal_id = response.css('.id-web p.id').extract_first().split(':')[1]
        item.add_value('internal_id', internal_id)

        # general desc
        description = response.css('div.descripcion p::text').extract_first()
        item.add_css('contact_info', 'div.info p::text')

        # extract feature list
        feature_names = list(map(lambda x: x.strip().lower()[:-1], response.css('div.caract ul li strong::text').extract())) + \
            list(map(lambda x: x.strip().lower()[:-1], response.css('div.caract ul:nth-child(2) li strong::text').extract()))
        
        # extract only odd values because of issue format getting values
        feature_values = list(
            map(
                lambda x: x.strip().lower(),
                response.css('div.caract ul li:not(strong)::text').extract())
                
        )[1::2] + \
            list(
                map(
                    lambda x: x.strip().lower(),
                    response.css('div.caract ul:nth-child(2) li:not(strong)::text').extract()
                )
            )

        # remove empty values before create dict
        feature_values = [v for v in feature_values if v != '']
        features = dict(zip(feature_names, feature_values))
        print(features)
        item.add_value('features', list(features.items()))

        if('estrato' in features.keys()):
            item.add_value('stratum', features['estrato'])
        elif('estrato' in description):
            item.add_value(
                'stratum', 
                re.match('(.*estrato )([\d]*)', description).group(1)
            )

        if('barrio' in features.keys()):
            item.add_value('neighborhood', features['barrio'])
        elif('barrio' in description):
            item.add_value(
                'neighborhood', 
                re.match('(.*barrio )([\S]*)', description).group(1)
            )

        if('área' in features.keys()):
            item.add_value('surface', features['área'])

        # process other features
        other_features = list(
            filter(
                (lambda x: x != ''),
                list(
                    map(
                        lambda x: x.strip(),
                        response.css('div.caract ul:nth-child(3) li::text').extract()
                    )
                )
            )
        )
        item.add_value('other_features', other_features)

        # extract other features from description text
        item.add_value('description', description)

        yield item.load_item()
