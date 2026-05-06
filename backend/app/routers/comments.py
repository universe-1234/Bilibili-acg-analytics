from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.comment import Comment
from ..models.video import Video
from ..models.user import User
from ..schemas.comment import CommentCreate, CommentOut, CommentListResponse
from ..middleware.auth_middleware import require_auth, get_current_user
from typing import Optional

router = APIRouter(prefix="/api/videos", tags=["评论"])


@router.get("/{video_id}/comments", response_model=CommentListResponse)
def get_comments(
    video_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")

    query = db.query(Comment, User).join(User, Comment.user_id == User.id).filter(
        Comment.video_id == video_id, Comment.parent_id.is_(None)
    )
    total = query.count()
    results = query.order_by(Comment.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    items = []
    for comment, user in results:
        co = CommentOut.model_validate(comment)
        co.username = user.username
        co.nickname = user.nickname
        items.append(co)

    return CommentListResponse(items=items, total=total, page=page, page_size=page_size)


@router.post("/{video_id}/comments", response_model=CommentOut)
def create_comment(
    video_id: int,
    data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_auth),
):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")
    if data.parent_id:
        parent = db.query(Comment).filter(Comment.id == data.parent_id).first()
        if not parent or parent.video_id != video_id:
            raise HTTPException(status_code=400, detail="父评论不存在")

    comment = Comment(
        user_id=current_user.id,
        video_id=video_id,
        content=data.content,
        parent_id=data.parent_id,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    co = CommentOut.model_validate(comment)
    co.username = current_user.username
    co.nickname = current_user.nickname
    return co


@router.get("/{video_id}/comments/{comment_id}/replies")
def get_replies(
    video_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
):
    query = db.query(Comment, User).join(User, Comment.user_id == User.id).filter(
        Comment.video_id == video_id, Comment.parent_id == comment_id
    )
    results = query.order_by(Comment.created_at).all()
    items = []
    for comment, user in results:
        co = CommentOut.model_validate(comment)
        co.username = user.username
        co.nickname = user.nickname
        items.append(co)
    return items
