from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.video import Video, UserFavorite
from ..models.user import User
from ..schemas.video import VideoOut, VideoListResponse
from ..middleware.auth_middleware import require_auth

router = APIRouter(prefix="/api/user", tags=["用户收藏"])


@router.get("/favorites", response_model=VideoListResponse)
def get_favorites(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_auth),
):
    query = db.query(Video).join(
        UserFavorite, UserFavorite.video_id == Video.id
    ).filter(UserFavorite.user_id == current_user.id)

    total = query.count()
    videos = query.offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for v in videos:
        vo = VideoOut.model_validate(v)
        vo.is_favorited = True
        items.append(vo)

    return VideoListResponse(items=items, total=total, page=page, page_size=page_size)
