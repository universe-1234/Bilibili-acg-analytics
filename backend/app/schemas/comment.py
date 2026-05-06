from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CommentCreate(BaseModel):
    content: str
    parent_id: Optional[int] = None


class CommentOut(BaseModel):
    id: int
    user_id: int
    video_id: int
    content: str
    parent_id: Optional[int] = None
    username: str = ""
    nickname: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CommentListResponse(BaseModel):
    items: List[CommentOut]
    total: int
    page: int
    page_size: int
