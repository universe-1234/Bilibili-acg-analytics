import json
import time
import scrapy
from datetime import datetime
from ..items import BilibiliVideoItem


class ACGSpider(scrapy.Spider):
    name = "acg_spider"
    allowed_domains = ["bilibili.com", "api.bilibili.com"]

    # ACG-related ranking category IDs
    # 1=动画, 168=国创, 4=游戏, 129=舞蹈
    RANKING_RIDS = [1, 168, 4, 129]

    def __init__(self, target_count=800, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_count = int(target_count)
        self.crawled_count = 0
        self.crawled_bvids = set()

    def start_requests(self):
        # Popular API - trending videos (pages 1-16, 50 per page = up to 800)
        for pn in range(1, 17):
            yield scrapy.Request(
                url=f"https://api.bilibili.com/x/web-interface/popular?pn={pn}&ps=50",
                callback=self.parse_popular,
                headers=self._api_headers(),
            )

    def _api_headers(self):
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.bilibili.com/",
            "Origin": "https://www.bilibili.com",
        }

    def parse_ranking(self, response):
        try:
            data = json.loads(response.text)
            if data.get("code") != 0:
                self.logger.error(f"Ranking API error: {data.get('message')}")
                return

            video_list = data.get("data", {}).get("list", [])
            rid = data.get("data", {}).get("rid", 0)
            rid_names = {1: "动画", 168: "国创", 4: "游戏", 129: "舞蹈"}
            category = rid_names.get(rid, "ACG")

            for video_data in video_list:
                if self.crawled_count >= self.target_count:
                    return

                bvid = video_data.get("bvid", "")
                if bvid in self.crawled_bvids:
                    continue

                item = self._parse_video(video_data, category)
                if item:
                    self.crawled_bvids.add(bvid)
                    self.crawled_count += 1
                    yield item

            self.logger.info(f"Ranking rid={rid}: {len(video_list)} videos, total crawled: {self.crawled_count}")

        except Exception as e:
            self.logger.error(f"Error parsing ranking: {e}")

    def parse_popular(self, response):
        try:
            data = json.loads(response.text)
            if data.get("code") != 0:
                self.logger.error(f"Popular API error: {data.get('message')}")
                return

            video_list = data.get("data", {}).get("list", [])
            for video_data in video_list:
                if self.crawled_count >= self.target_count:
                    return

                bvid = video_data.get("bvid", "")
                if bvid in self.crawled_bvids:
                    continue

                item = self._parse_video(video_data, "ACG")
                if item:
                    self.crawled_bvids.add(bvid)
                    self.crawled_count += 1
                    yield item

            self.logger.info(f"Popular: {len(video_list)} videos, total crawled: {self.crawled_count}")

        except Exception as e:
            self.logger.error(f"Error parsing popular: {e}")

    def _parse_video(self, video_data, category):
        item = BilibiliVideoItem()
        bvid = video_data.get("bvid", "")

        item["bv_id"] = bvid
        item["title"] = video_data.get("title", "").replace('<em class="keyword">', "").replace("</em>", "")
        item["description"] = video_data.get("desc", "")
        item["cover_url"] = (video_data.get("pic", "") or "").replace("http:", "https:")
        item["duration"] = self._format_duration(video_data.get("duration", 0))

        stats = video_data.get("stat", {})
        item["play_count"] = stats.get("view", 0)
        item["danmaku_count"] = stats.get("danmaku", 0)
        item["like_count"] = stats.get("like", 0)
        item["coin_count"] = stats.get("coin", 0)
        item["favorite_count"] = stats.get("favorite", 0)
        item["share_count"] = stats.get("share", 0)
        item["reply_count"] = stats.get("reply", 0)

        owner = video_data.get("owner", {})
        item["author_name"] = owner.get("name", "")
        item["author_id"] = str(owner.get("mid", ""))

        item["category"] = category
        item["bilibili_url"] = f"https://www.bilibili.com/video/{bvid}"

        pubdate = video_data.get("pubdate")
        if pubdate:
            try:
                item["publish_date"] = datetime.fromtimestamp(pubdate)
            except (ValueError, OSError):
                item["publish_date"] = datetime.now()

        item["tags"] = video_data.get("tname", "")

        return item

    @staticmethod
    def _format_duration(seconds):
        if not seconds or seconds <= 0:
            return "00:00"
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        if h > 0:
            return f"{h:02d}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"
