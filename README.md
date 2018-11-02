# house-scooby
Python based  web scrapper

* Python 3.6.5
* Scrapy

## How to ##
 ```
    python -m virtualenv env
    source env/bin/activate
    pip install -r requirements.txt
    cd scrapper/
    ## single spider
    scrapy crawl finca_raiz

    ## all the spiders
    python scrapper/runner.py 
 ```

## Resources ##
* (User agent setting config)[https://www.simplified.guide/scrapy/change-user-agent]
