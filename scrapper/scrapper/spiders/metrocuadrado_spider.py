# -*- coding: utf-8 -*-

from scrapy import Spider, Request, FormRequest
from scrapy.loader import ItemLoader
import re

# custom item definition
from scrapper.items import PropertyItem

CITIES = ['cali', 'jamundi', 'palmira']


class MetroCuadradoSpider(Spider):
    name = "metro_cuadrado"
    allowed_domains = ["metrocuadrado.com"]

    def __init__(self, max_prixe='100000000', **kwargs):
        self.max_price = max_prixe
        super().__init__(**kwargs)

    def start_requests(self):
        base_url = 'http://www.metrocuadrado.com/search/list/ajax?mvalorventa=0-{0}&mciudad={1}&mtiponegocio=venta&mtipoinmueble=casa;lote;apartamento&selectedLocationCategory=1&selectedLocationFilter=mciudad&currentPage=1&totalPropertiesCount=1410&totalUsedPropertiesCount=1366&totalNewPropertiesCount=44&sfh=1'
        self.start_urls = [base_url.format(self.max_price, c) for c in CITIES]
        return [FormRequest(url, method='POST', callback=self.parse) for url in self.start_urls]

    def parse(self, response):
        for item in response.css('div#main .m_rs_list_item'):
            property_item = ItemLoader(item=PropertyItem(), response=response)
            name = item.css(
                'div.detail_wrap .m_rs_list_item_main .header h2::text').extract_first()
            description = item.css(
                'div.detail_wrap .m_rs_list_item_details .desc p:last-child::text').extract_first()
            city = name.split(' ')[-1]

            property_item.add_value('name', name)
            property_item.add_value('city', city)
            property_item.add_value('description', description)

            property_url = response.urljoin(
                item.css('div.detail_wrap .m_rs_list_item_main .header a.data-details-id::attr(href)').extract_first())

            property_item.add_value('link', property_url)
            property_item.add_value('surface', item.css(
                'div.detail_wrap .m_rs_list_item_main .m2 p>span:nth-child(2)::text').extract_first())

            # call single element page
            request = Request(property_url, self.parse_single,
                              meta={'loader': property_item})
            yield request

        current_url = response.request.url
        next_page_pattern = r"(.*currentPage=)(\d+)"
        next_page = str(
            int(re.match(next_page_pattern, current_url).group(2)) + 1)
        next_url = re.sub(next_page_pattern, fr"\g<1>{next_page}", current_url)
        if next_url is not None:
            next_url = response.urljoin(next_url)
            yield FormRequest(next_url, method='POST', callback=self.parse)

    def parse_single(self, response):
        item = response.meta['loader']
        feature_names = response.css('div.m_property_info_details:not(.more_info)>dl dt>h3::text').extract()
        feature_values = [v for v in response.css('div.m_property_info_details:not(.more_info)>dl dd>h4::text').extract() if v.strip() != '']
        features_dict = dict(zip(feature_names, feature_values))
        
        item.add_value('internal_id', features_dict.pop('Código web', ''))
        item.add_value('neighborhood', features_dict.pop('Nombre común del barrio ', ''))
        item.add_value('stratum', features_dict.pop('Estrato', ''))
        item.add_value('parking_spots', features_dict.pop('Parqueadero', ''))
        item.add_value('bedrooms', features_dict.pop('Habitaciones', ''))
        item.add_value('bathrooms', features_dict.pop('Baños', ''))
        item.add_value('floor_location', features_dict.pop('Número de piso', '1'))
        item.add_value('antiquity', features_dict.pop('Tiempo de construido', ''))

        price = response.css('dl.price dd::text').extract_first()
        item.add_value('price', price)

        extra_feature_names = response.css('div.m_property_info_details.more_info>dl dt>h3::text').extract()
        extra_feature_values = response.css('div.m_property_info_details.more_info>dl dd>h4::text').extract()
        extra_features_dict = dict(zip(extra_feature_names, extra_feature_values))
        item.add_value('features',  extra_features_dict)

        yield item.load_item()
