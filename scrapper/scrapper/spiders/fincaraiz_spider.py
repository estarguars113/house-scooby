# -*- coding: utf-8 -*-

from scrapy import Spider, Request
import re


class FincaRaizSpider(Spider):
    name = "finca_raiz"
    allowd_domains = ["fincaraiz.com.co"]
    # types = ['apartamento', 'casa-lote', 'casa-campestre', 'casa', 'lote', 'finca']
    types = ['casa']
    cities = ['cali']
    # cities = ['cali', 'jamundi', 'palmira']
    min_price = '60000000'
    max_price = '190000000'
   
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
            # clean input data
            description = item.css('li.title-grid .span-title>a h2.h2-grid::text').extract_first() or \
                item.css('li.information .title-grid a::attr(title)').extract_first()

            surface = item.css('li.surface::text').extract_first() or \
                item.css('li.information .title-grid .description::text').extract_first()

            price = item.css('li.price div:first-child meta::attr(content)').extract_first() or \
                item.css('li.information .title-grid .descriptionPrice::text').extract_first()

            full_location = item.css('li.title-grid .span-title>a>div:last-child::text').extract_first()
            neighborhood, city = full_location.split('-') if full_location else ["", ""]

            yield {
                'link':  response.urljoin(item.css('li.title-grid .span-title>a::attr(href)').extract_first()),
                'description': description,
                'surface':  surface,
                'price':    price,
                'rooms': item.css('li.surface>div::text').extract_first(),
                'neighborhood': neighborhood,
                'city': city,
                'status': item.css('li.media .usedMark::text').extract_first() or 'Nuevo',
            }

        current_url = response.request.url
        next_page_pattern = r"(.*ad=30\|)(\d+)"
        next_page = str(
            int(re.match(next_page_pattern, current_url).group(2)) + 1)

        print('next: ' + next_page)

        next_url = re.sub(next_page_pattern, fr'\g<1>{next_page}', current_url)
        if next_url is not None:
            next_url = response.urljoin(next_url)
            yield Request(next_url, self.parse)