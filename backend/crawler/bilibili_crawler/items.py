import scrapy


class BilibiliVideoItem(scrapy.Item):
    bv_id = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    cover_url = scrapy.Field()
    play_count = scrapy.Field()
    danmaku_count = scrapy.Field()
    like_count = scrapy.Field()
    coin_count = scrapy.Field()
    favorite_count = scrapy.Field()
    share_count = scrapy.Field()
    reply_count = scrapy.Field()
    duration = scrapy.Field()
    author_name = scrapy.Field()
    author_id = scrapy.Field()
    category = scrapy.Field()
    tags = scrapy.Field()
    publish_date = scrapy.Field()
    bilibili_url = scrapy.Field()
