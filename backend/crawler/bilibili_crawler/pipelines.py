import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.database import SessionLocal
from app.models.video import Video


class MySQLPipeline:
    def __init__(self):
        self.db = None

    def open_spider(self, spider):
        self.db = SessionLocal()

    def close_spider(self, spider):
        if self.db:
            self.db.close()

    def process_item(self, item, spider):
        existing = self.db.query(Video).filter(Video.bv_id == item["bv_id"]).first()
        if existing:
            for field, value in item.items():
                if value is not None and hasattr(existing, field):
                    setattr(existing, field, value)
            self.db.commit()
            spider.logger.info(f"Updated: {item['title']}")
            return item

        video = Video(
            bv_id=item.get("bv_id", ""),
            title=item.get("title", ""),
            description=item.get("description", ""),
            cover_url=item.get("cover_url", ""),
            play_count=item.get("play_count", 0),
            danmaku_count=item.get("danmaku_count", 0),
            like_count=item.get("like_count", 0),
            coin_count=item.get("coin_count", 0),
            favorite_count=item.get("favorite_count", 0),
            share_count=item.get("share_count", 0),
            reply_count=item.get("reply_count", 0),
            duration=item.get("duration", "00:00"),
            author_name=item.get("author_name", ""),
            author_id=item.get("author_id", ""),
            category=item.get("category", "ACG"),
            tags=item.get("tags", ""),
            publish_date=item.get("publish_date"),
            bilibili_url=item.get("bilibili_url", ""),
        )
        self.db.add(video)
        self.db.commit()
        spider.logger.info(f"Saved: {item['title']}")
        return item
