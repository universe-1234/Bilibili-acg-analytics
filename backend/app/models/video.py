from sqlalchemy import Column, Integer, String, DateTime, Text, BigInteger, Float
from sqlalchemy.sql import func
from ..database import Base


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    bv_id = Column(String(20), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, default="")
    cover_url = Column(String(500), default="")
    play_count = Column(BigInteger, default=0)
    danmaku_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    coin_count = Column(Integer, default=0)
    favorite_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    reply_count = Column(Integer, default=0)
    duration = Column(String(20), default="00:00")
    author_name = Column(String(100), default="")
    author_id = Column(String(50), default="")
    category = Column(String(50), default="ACG")
    tags = Column(String(500), default="")
    publish_date = Column(DateTime, nullable=True)
    bilibili_url = Column(String(500), default="")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class UserFavorite(Base):
    __tablename__ = "user_favorites"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    video_id = Column(Integer, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())


class VideoStatsHistory(Base):
    __tablename__ = "video_stats_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(Integer, nullable=False, index=True)
    play_count = Column(BigInteger, default=0)
    danmaku_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    favorite_count = Column(Integer, default=0)
    recorded_at = Column(DateTime, server_default=func.now(), index=True)
