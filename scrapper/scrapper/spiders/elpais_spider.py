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
            property_item = ItemLoader(
                item=PropertyItem(),
                response=response,
                selector=item
            )
            property_url = response.urljoin(item.css('div.info>a.link-info::attr(href)').extract_first())
            property_item.add_value('link', property_url)
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
        description = response.css('div.descripcion p::text').extract()
        item.add_css('contact_info', 'div.info p::text')

        # price
        item.add_value('price', response.css('p.precio::text').extract_first())

        # extract feature list
        feature_names = list(map(lambda x: x.strip().lower()[:-1], response.css('div.caract ul li strong::text').extract()))
        feature_names_2 = list(map(lambda x: x.strip().lower()[:-1], response.css('div.caract ul:nth-child(2) li strong::text').extract()))
        
        # extract only odd values because of issue format getting values
        feature_values = list(
            map(
                lambda x: x.strip().lower(),
                response.css('div.caract ul li:not(strong)::text').extract()
            )  
        )[1::2]

        feature_values_2 = list(
            map(
                lambda x: x.strip().lower(),
                response.css('div.caract ul:nth-child(2) li:not(strong)::text').extract()
            )
        )[1::2]

        # remove empty values before create dict
        feature_values = [v for v in feature_values if v != '']
        features = {**dict(
                zip(feature_names, feature_values)
            ), 
            **dict(
                zip(feature_names_2, feature_values_2)
            )}
       
        features_keys = features.keys()
        if('ciudad' in features_keys):
            item.add_value('city', features['ciudad'])
            features.pop('ciudad')

        if('no. de alcobas' in features_keys):
            item.add_value('bedrooms', features['no. de alcobas'])
            features.pop('no. de alcobas')

        if('no. de baños' in features_keys):
            item.add_value('bathrooms', features['no. de baños'])
            features.pop('no. de baños')

        if('estrato' in features_keys):
            item.add_value('stratum', features['estrato'])
            features.pop('estrato')
        elif('estrato' in description):
            item.add_value(
                'stratum', 
                re.match('(.*estrato )([\d]*)', description).group(1)
            )

        if('barrio' in features_keys):
            item.add_value('neighborhood', features['barrio'])
            features.pop('barrio')
        elif('barrio' in description):
            item.add_value(
                'neighborhood', 
                re.match('(.*barrio )([\S]*)', description).group(1)
            )

        if('área' in features_keys):
            item.add_value('surface', features['área'].replace(",", "."))
            features.pop('área')

        if('condición' in features_keys):
            item.add_value('status', features['condición'])
            features.pop('condición')

        if('no. de plantas' in features_keys):
            item.add_value('total_levels', features['no. de plantas'])
            features.pop('no. de plantas')

        if('tiempo construido' in features_keys):
            item.add_value('antiquity', features['tiempo construido'])
            features.pop('tiempo construido')

        item.add_value('features', list(features.items()))

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
