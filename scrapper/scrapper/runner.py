from spiders.fincaraiz_spider import FincaRaizSpider
from spiders.elpais_spider import ElPaisSpider
from spiders.metrocuadrado_spider import MetroCuadradoSpider
from spiders.vivendo_spider import vivendoSpider

# scrapy api
import scrapy
from scrapy.crawler import CrawlerProcess

process = CrawlerProcess({
  'DOWNLOAD_DELAY': 5,
  'RANDOMIZE_DOWNLOAD_DELAY': True,
  'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
  'FEED_FORMAT': 'csv',
  'FEED_URI': 'result.csv'
})
process.crawl(ElPaisSpider)
process.crawl(FincaRaizSpider)
process.crawl(MetroCuadradoSpider)
process.crawl(vivendoSpider)
process.start()