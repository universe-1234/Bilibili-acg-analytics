from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, or_
from typing import Optional
from ..database import get_db
from ..models.video import Video, UserFavorite, VideoStatsHistory
from ..models.user import User
from ..schemas.video import VideoOut, VideoListResponse
from ..middleware.auth_middleware import get_current_user, require_auth

router = APIRouter(prefix="/api/videos", tags=["视频"])


@router.get("", response_model=VideoListResponse)
def get_videos(
    keyword: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    sort_by: str = Query("play_count"),
    order: str = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    query = db.query(Video)
    if keyword:
        query = query.filter(
            or_(
                Video.title.contains(keyword),
                Video.description.contains(keyword),
                Video.tags.contains(keyword),
                Video.author_name.contains(keyword),
            )
        )
    if category:
        query = query.filter(Video.category == category)

    sort_field = getattr(Video, sort_by, Video.play_count)
    if order == "asc":
        query = query.order_by(asc(sort_field))
    else:
        query = query.order_by(desc(sort_field))

    total = query.count()
    videos = query.offset((page - 1) * page_size).limit(page_size).all()

    favorited_ids = set()
    if current_user:
        favs = db.query(UserFavorite.video_id).filter(
            UserFavorite.user_id == current_user.id
        ).all()
        favorited_ids = {f[0] for f in favs}

    items = []
    for v in videos:
        vo = VideoOut.model_validate(v)
        vo.is_favorited = v.id in favorited_ids
        items.append(vo)

    return VideoListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    results = db.query(Video.category).distinct().all()
    return [r[0] for r in results if r[0]]


@router.get("/{video_id}", response_model=VideoOut)
def get_video_detail(
    video_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")
    vo = VideoOut.model_validate(video)
    if current_user:
        fav = db.query(UserFavorite).filter(
            UserFavorite.user_id == current_user.id,
            UserFavorite.video_id == video_id,
        ).first()
        vo.is_favorited = fav is not None
    return vo


@router.post("/{video_id}/favorite")
def toggle_favorite(
    video_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_auth),
):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")
    fav = db.query(UserFavorite).filter(
        UserFavorite.user_id == current_user.id,
        UserFavorite.video_id == video_id,
    ).first()
    if fav:
        db.delete(fav)
        db.commit()
        return {"favorited": False}
    else:
        db.add(UserFavorite(user_id=current_user.id, video_id=video_id))
        db.commit()
        return {"favorited": True}


@router.get("/{video_id}/history")
def get_video_history(video_id: int, db: Session = Depends(get_db)):
    history = db.query(VideoStatsHistory).filter(
        VideoStatsHistory.video_id == video_id
    ).order_by(VideoStatsHistory.recorded_at).all()
    return [
        {
            "play_count": h.play_count,
            "danmaku_count": h.danmaku_count,
            "like_count": h.like_count,
            "recorded_at": h.recorded_at.isoformat(),
        }
        for h in history
    ]
