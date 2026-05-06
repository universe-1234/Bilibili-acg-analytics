"""
Standalone crawler runner.
Usage: python run_crawler.py [target_count]

Examples:
    python run_crawler.py          # default 800 videos
    python run_crawler.py 100     # crawl 100 videos
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

try:
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings
except ImportError:
    raise ImportError(
        "Scrapy is required to run this crawler. Install it with 'pip install scrapy'."
    )

from bilibili_crawler.spiders.acg_spider import ACGSpider


def main():
    target = int(sys.argv[1]) if len(sys.argv) > 1 else 800
    print(f"Starting crawler, target: {target} videos")

    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl(ACGSpider, target_count=target)
    process.start()
    print("Crawl finished!")


if __name__ == "__main__":
    main()
