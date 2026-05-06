from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class VideoOut(BaseModel):
    id: int
    bv_id: str
    title: str
    description: Optional[str] = None
    cover_url: Optional[str] = None
    play_count: int = 0
    danmaku_count: int = 0
    like_count: int = 0
    coin_count: int = 0
    favorite_count: int = 0
    share_count: int = 0
    reply_count: int = 0
    duration: str = "00:00"
    author_name: str = ""
    author_id: str = ""
    category: str = "ACG"
    tags: str = ""
    publish_date: Optional[datetime] = None
    bilibili_url: str = ""
    is_favorited: Optional[bool] = False

    class Config:
        from_attributes = True


class VideoListResponse(BaseModel):
    items: List[VideoOut]
    total: int
    page: int
    page_size: int


class VideoSearchParams(BaseModel):
    keyword: Optional[str] = None
    category: Optional[str] = None
    sort_by: str = "play_count"
    order: str = "desc"
    page: int = 1
    page_size: int = 20
