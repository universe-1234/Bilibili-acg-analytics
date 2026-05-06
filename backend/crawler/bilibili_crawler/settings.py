BOT_NAME = "bilibili_acg_crawler"
SPIDER_MODULES = ["bilibili_crawler.spiders"]
NEWSPIDER_MODULE = "bilibili_crawler.spiders"

ROBOTSTXT_OBEY = False
CONCURRENT_REQUESTS = 8
DOWNLOAD_DELAY = 1.5
RANDOMIZE_DOWNLOAD_DELAY = True
CONCURRENT_REQUESTS_PER_DOMAIN = 4

COOKIES_ENABLED = True

DEFAULT_REQUEST_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://www.bilibili.com/",
}

DOWNLOADER_MIDDLEWARES = {
    "bilibili_crawler.middlewares.RotateUserAgentMiddleware": 400,
    "bilibili_crawler.middlewares.RequestDelayMiddleware": 500,
}

ITEM_PIPELINES = {
    "bilibili_crawler.pipelines.MySQLPipeline": 300,
}

# Disable for standalone crawl runs
# TELNETCONSOLE_ENABLED = False

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 2
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0

RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

DOWNLOAD_TIMEOUT = 30
