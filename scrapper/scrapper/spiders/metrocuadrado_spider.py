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

    def __init__(self, max_prixe='10000000', **kwargs):
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
            city = name.split(' ')[-1]

            property_item.add_value('name', name)
            property_item.add_value('city', city)

            property_url = response.urljoin(
                item.css('div.detail_wrap .m_rs_list_item_main .header a.data-details-id::attr(href)').extract_first())
            
            property_item.add_value('link', property_url)
            property_item.add_css('surface', 'div.detail_wrap .m_rs_list_item_main .price_desc .m2 span:nth-child(2)::text')
            property_item.add_css('bedrooms', 'div.detail_wrap .m_rs_list_item_main .price_desc .rooms span:nth-child(2)::text')
            property_item.add_css('bathrooms', 'div.detail_wrap .m_rs_list_item_main .price_desc .bathrooms span:nth-child(2)::text')
            property_item.add_css('price', 'div.detail_wrap .m_rs_list_item_main .price_desc p.price span:nth-child(2)::text')
            property_item.add_css('description', 'div.detail_wrap .m_rs_list_item_details .desc p:last-child::text')
            
            # call single element page
            request = Request(property_url, self.parse_single)
            request.meta['loader'] = property_item
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
        item.add_css('internal_id', 'div.m_property_info_details:not(.more_info)>dl:nth-child(2) dd>h4::text')
        item.add_css('description', '#pDescription::text')
        item.add_css('neighborhood', 'div.m_property_info_details:not(.more_info)>dl:nth-child(3) dd>h4::text')
        item.add_css('stratum', 'div.m_property_info_details:not(.more_info)>dl:nth-child(4) dd>h4::text')
        item.add_css('surface', 'div.m_property_info_details:not(.more_info)>dl:nth-child(6) dd>h4::text')
        item.add_css('status', 'div.m_property_info_details:not(.more_info)>dl:nth-child(8) dd>h4::text')
        item.add_css('parking_spots', 'div.m_property_info_table>dl:last-child dd::text')
        
        item.add_css('features', 'div.m_property_info_details.services ul li::text')

        yield item.load_item()
