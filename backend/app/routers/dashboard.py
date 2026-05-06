from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from ..database import get_db
from ..models.video import Video, UserFavorite, VideoStatsHistory
from ..models.comment import Comment
from ..models.user import User

router = APIRouter(prefix="/api/dashboard", tags=["数据看板"])


@router.get("/overview")
def get_overview(db: Session = Depends(get_db)):
    total_videos = db.query(func.count(Video.id)).scalar() or 0
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_comments = db.query(func.count(Comment.id)).scalar() or 0
    total_plays = db.query(func.sum(Video.play_count)).scalar() or 0
    total_likes = db.query(func.sum(Video.like_count)).scalar() or 0
    total_danmaku = db.query(func.sum(Video.danmaku_count)).scalar() or 0
    total_favorites = db.query(func.count(UserFavorite.id)).scalar() or 0

    return {
        "total_videos": total_videos,
        "total_users": total_users,
        "total_comments": total_comments,
        "total_plays": total_plays,
        "total_likes": total_likes,
        "total_danmaku": total_danmaku,
        "total_favorites": total_favorites,
    }


@router.get("/category-stats")
def get_category_stats(db: Session = Depends(get_db)):
    results = db.query(
        Video.category,
        func.count(Video.id).label("count"),
        func.sum(Video.play_count).label("total_plays"),
        func.sum(Video.like_count).label("total_likes"),
        func.avg(Video.play_count).label("avg_plays"),
    ).filter(Video.category != "").group_by(Video.category).all()

    return [
        {
            "category": r[0],
            "count": r[1],
            "total_plays": r[2] or 0,
            "total_likes": r[3] or 0,
            "avg_plays": round(r[4] or 0, 0),
        }
        for r in results
    ]


@router.get("/top-videos")
def get_top_videos(limit: int = 20, db: Session = Depends(get_db)):
    videos = db.query(Video).order_by(desc(Video.play_count)).limit(limit).all()
    return [
        {
            "id": v.id,
            "title": v.title,
            "play_count": v.play_count,
            "like_count": v.like_count,
            "danmaku_count": v.danmaku_count,
            "cover_url": v.cover_url,
            "author_name": v.author_name,
        }
        for v in videos
    ]


@router.get("/daily-trends")
def get_daily_trends(days: int = 30, db: Session = Depends(get_db)):
    from sqlalchemy import cast, Date, text
    stats = db.query(
        func.date(VideoStatsHistory.recorded_at).label("date"),
        func.sum(VideoStatsHistory.play_count).label("plays"),
        func.sum(VideoStatsHistory.like_count).label("likes"),
        func.sum(VideoStatsHistory.danmaku_count).label("danmaku"),
    ).group_by("date").order_by("date").limit(days).all()

    return [
        {
            "date": str(s[0]),
            "plays": s[1] or 0,
            "likes": s[2] or 0,
            "danmaku": s[3] or 0,
        }
        for s in stats
    ]


@router.get("/video-engagement")
def get_video_engagement(db: Session = Depends(get_db)):
    videos = db.query(
        Video.title,
        Video.play_count,
        Video.like_count,
        Video.danmaku_count,
        Video.favorite_count,
        Video.share_count,
        Video.coin_count,
    ).order_by(desc(Video.play_count)).limit(30).all()

    return [
        {
            "title": v[0][:20] + "..." if len(v[0]) > 20 else v[0],
            "plays": v[1],
            "likes": v[2],
            "danmaku": v[3],
            "favorites": v[4],
            "shares": v[5],
            "coins": v[6],
        }
        for v in videos
    ]


@router.get("/tag-cloud")
def get_tag_cloud(db: Session = Depends(get_db)):
    videos = db.query(Video.tags).filter(Video.tags != "").all()
    tag_count = {}
    for (tags_str,) in videos:
        for tag in tags_str.split(","):
            t = tag.strip()
            if t:
                tag_count[t] = tag_count.get(t, 0) + 1
    sorted_tags = sorted(tag_count.items(), key=lambda x: x[1], reverse=True)[:50]
    return [{"name": t[0], "value": t[1]} for t in sorted_tags]


@router.get("/author-ranking")
def get_author_ranking(db: Session = Depends(get_db)):
    results = db.query(
        Video.author_name,
        func.count(Video.id).label("video_count"),
        func.sum(Video.play_count).label("total_plays"),
        func.sum(Video.like_count).label("total_likes"),
    ).filter(Video.author_name != "").group_by(Video.author_name).order_by(
        desc(func.sum(Video.play_count))
    ).limit(20).all()

    return [
        {
            "author": r[0],
            "video_count": r[1],
            "total_plays": r[2] or 0,
            "total_likes": r[3] or 0,
        }
        for r in results
    ]


@router.get("/publish-trends")
def get_publish_trends(db: Session = Depends(get_db)):
    results = db.query(
        func.date(Video.publish_date).label("date"),
        func.count(Video.id).label("count"),
    ).filter(Video.publish_date.isnot(None)).group_by("date").order_by("date").all()

    return [{"date": str(r[0]), "count": r[1]} for r in results]


@router.get("/engagement-analysis")
def get_engagement_analysis(db: Session = Depends(get_db)):
    """Per-category engagement rates for deeper analysis"""
    results = db.query(
        Video.category,
        func.count(Video.id).label("count"),
        func.sum(Video.play_count).label("plays"),
        func.sum(Video.like_count).label("likes"),
        func.sum(Video.danmaku_count).label("danmaku"),
        func.sum(Video.reply_count).label("replies"),
        func.sum(Video.coin_count).label("coins"),
        func.sum(Video.favorite_count).label("favorites"),
        func.sum(Video.share_count).label("shares"),
    ).filter(Video.category != "").group_by(Video.category).all()

    def safe_rate(numerator, denominator):
        if not denominator or denominator == 0:
            return 0
        return round(numerator / denominator * 100, 2)

    return [
        {
            "category": r[0],
            "video_count": r[1],
            "total_plays": r[2] or 0,
            "total_danmaku": r[4] or 0,
            "total_likes": r[3] or 0,
            "total_replies": r[5] or 0,
            "total_coins": r[6] or 0,
            "total_favorites": r[7] or 0,
            "total_shares": r[8] or 0,
            "like_rate": safe_rate(r[3], r[2]),
            "danmaku_rate": safe_rate(r[4], r[2]),
            "reply_rate": safe_rate(r[5], r[2]),
            "coin_rate": safe_rate(r[6], r[2]),
            "favorite_rate": safe_rate(r[7], r[2]),
            "share_rate": safe_rate(r[8], r[2]),
            "engagement_score": round(safe_rate(r[3], r[2]) * 0.35 + safe_rate(r[4], r[2]) * 0.2 + safe_rate(r[5], r[2]) * 0.2 + safe_rate(r[6], r[2]) * 0.15 + safe_rate(r[8], r[2]) * 0.1, 2),
        }
        for r in results
        if r[2] and r[2] > 0
    ]


@router.get("/duration-analysis")
def get_duration_analysis(db: Session = Depends(get_db)):
    """Analyze video duration buckets vs avg performance"""
    videos = db.query(
        Video.duration, Video.play_count, Video.like_count, Video.danmaku_count
    ).all()

    buckets = {
        "<1分钟": {"count": 0, "plays": 0, "likes": 0, "danmaku": 0},
        "1-3分钟": {"count": 0, "plays": 0, "likes": 0, "danmaku": 0},
        "3-10分钟": {"count": 0, "plays": 0, "likes": 0, "danmaku": 0},
        "10-30分钟": {"count": 0, "plays": 0, "likes": 0, "danmaku": 0},
        ">30分钟": {"count": 0, "plays": 0, "likes": 0, "danmaku": 0},
    }

    for dur_str, plays, likes, danmaku in videos:
        secs = parse_duration(dur_str)
        if secs < 60:
            bucket = "<1分钟"
        elif secs < 180:
            bucket = "1-3分钟"
        elif secs < 600:
            bucket = "3-10分钟"
        elif secs < 1800:
            bucket = "10-30分钟"
        else:
            bucket = ">30分钟"
        buckets[bucket]["count"] += 1
        buckets[bucket]["plays"] += (plays or 0)
        buckets[bucket]["likes"] += (likes or 0)
        buckets[bucket]["danmaku"] += (danmaku or 0)

    return [
        {
            "bucket": name,
            "count": d["count"],
            "avg_plays": round(d["plays"] / d["count"]) if d["count"] > 0 else 0,
            "avg_likes": round(d["likes"] / d["count"]) if d["count"] > 0 else 0,
            "avg_danmaku": round(d["danmaku"] / d["count"]) if d["count"] > 0 else 0,
        }
        for name, d in buckets.items()
        if d["count"] > 0
    ]


def parse_duration(dur_str):
    """Parse 'HH:MM:SS' or 'MM:SS' to seconds"""
    if not dur_str:
        return 0
    parts = dur_str.strip().split(":")
    if len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    elif len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    return 0
