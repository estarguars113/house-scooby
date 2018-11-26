from scrapper.spiders.fincaraiz_spider import FincaRaizSpider
from scrapper.spiders.elpais_spider import ElPaisSpider
from scrapper.spiders.metrocuadrado_spider import MetroCuadradoSpider
from scrapper.spiders.vivendo_spider import vivendoSpider

# scrapy api
import scrapy
from scrapy.crawler import CrawlerProcess

process = CrawlerProcess({
  'DOWNLOAD_DELAY': 5,
  'RANDOMIZE_DOWNLOAD_DELAY': True,
  'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
  'FEED_FORMAT': 'jsonlines',
  'FEED_URI': 'result.jsonl'
})

kwargs = { 'max_price': '300000000' }

process.crawl(ElPaisSpider)
process.crawl(FincaRaizSpider, **kwargs)
process.crawl(MetroCuadradoSpider, **kwargs)
process.crawl(vivendoSpider)
process.start()