BOT_NAME = 'arrow'

SPIDER_MODULES = ['arrow.spiders']
NEWSPIDER_MODULE = 'arrow.spiders'


# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 100

# Disable cookies (enabled by default)
COOKIES_ENABLED = False


ITEM_PIPELINES = {
   'arrow.pipelines.SQLITE_Pipeline': 300,
}

DOWNLOADER_MIDDLEWARES = {
    'scrapy_crawlera.CrawleraMiddleware': 610,
}

CRAWLERA_ENABLED = True
CRAWLERA_APIKEY = 'c79ed6d3bb814597b4b26b17dfa299d5'
DOWNLOADER_MIDDLEWARES = {'scrapy_crawlera.CrawleraMiddleware': 610}
CRAWLERA_PRESERVE_DELAY = 5

LOG_LEVEL = 'INFO'
RETRY_TIMES = 50
RETRY_HTTP_CODES = [424, 403]

# DOWNLOADER_MIDDLEWARES = {
#     #'Helloraye.middlewares.HellorayeDownloaderMiddleware': 543,
#     'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
#     'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
#     'scrapy.downloadermiddlewares.retry.RetryMiddleware': 500,
#     'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
#     #'scrapy_crawlera.CrawleraMiddleware': 610,
# }

# CONCURRENT_REQUESTS_PER_DOMAIN = 500000
# CONCURRENT_REQUESTS_PER_IP = 1
# RETRY_TIMES=50

# ROTATING_PROXY_LIST_PATH = 'proxy.txt'
# ROTATING_PROXY_PAGE_RETRY_TIMES=50


# BRIGHTDATA_ENABLED = True
# BRIGHTDATA_URL = 'http://127.0.0.1:24000'
# DOWNLOADER_MIDDLEWARES = {'scrapyx_bright_data.BrightDataProxyMiddleware': 610}