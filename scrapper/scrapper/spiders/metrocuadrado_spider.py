# -*- coding: utf-8 -*-

from scrapy import Spider, Request, FormRequest
import re
cities = ['cali', 'jamundi', 'palmira']
max_price = '200000000'
base_url = 'http://www.metrocuadrado.com/search/list/ajax?mvalorventa=0-{0}&mciudad={1}&mtiponegocio=venta&mtipoinmueble=casa;lote;apartamento&selectedLocationCategory=1&selectedLocationFilter=mciudad&currentPage=1&totalPropertiesCount=1410&totalUsedPropertiesCount=1366&totalNewPropertiesCount=44&sfh=1'


class MetroCuadradoSpider(Spider):
    name = "metro_cuadrado"
    allowed_domains = ["metrocuadrado.com"]
    start_urls = [base_url.format(max_price, c) for c in cities]

    def start_requests(self):
        return [FormRequest(url, method='POST', callback=self.parse) for url in self.start_urls]

    def parse(self, response):
        for item in response.css('div#main .m_rs_list_item'):
            name = item.css(
                'div.detail_wrap .m_rs_list_item_main .header h2::text').extract_first()
            city = name.split(' ')[-1]
            property_url = response.urljoin(
                item.css('div.detail_wrap .m_rs_list_item_main .header a.data-details-id::attr(href)').extract_first())
            surface = item.css(
                'div.detail_wrap .m_rs_list_item_main .price_desc .m2 span:nth-child(2)::text').extract_first()
            rooms = item.css(
                'div.detail_wrap .m_rs_list_item_main .price_desc .rooms span:nth-child(2)::text').extract_first()
            bathrooms = item.css(
                'div.detail_wrap .m_rs_list_item_main .price_desc .bathrooms span:nth-child(2)::text').extract_first()
            price = item.css(
                'div.detail_wrap .m_rs_list_item_main .price_desc p.price span:nth-child(2)::text').extract_first()
            description = item.css(
                'div.detail_wrap .m_rs_list_item_details .desc p:last-child::text').extract_first()

            property_item = {
                'name': name,
                'description': description,
                'link':  property_url,
                'surface': surface,
                'price': price,
                'rooms': rooms,
                'bathrooms': bathrooms,
                'city': city
            }
            # call single element page
            yield Request(url=property_url, callback=self.parse_single, meta=dict(item=property_item))
        
        current_url = response.request.url
        next_page_pattern = r"(.*currentPage=)(\d+)"
        next_page = str(
            int(re.match(next_page_pattern, current_url).group(2)) + 1)
        next_url = re.sub(next_page_pattern, fr"\g<1>{next_page}", current_url)
        if next_url is not None:
            next_url = response.urljoin(next_url)
            yield FormRequest(next_url, method='POST', callback=self.parse)

    def parse_single(self, response):
        item = response.meta['item']
        item['code'] = response.css(
            'div.m_property_info_details:not(.more_info)>dl:first-of-type dd>h4::text').extract_first()

        yield item
