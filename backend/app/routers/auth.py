from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from ..database import get_db
from ..schemas.user import UserRegister, UserLogin, UserOut, Token, ProfileUpdate, PasswordChange, UserStats
from ..services.auth_service import register_user, authenticate_user, create_access_token, hash_password, verify_password
from ..middleware.auth_middleware import require_auth
from ..models.user import User
from ..models.comment import Comment
from ..models.video import UserFavorite

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/register", response_model=Token)
def register(data: UserRegister, db: Session = Depends(get_db)):
    user = register_user(db, data)
    if user is None:
        raise HTTPException(status_code=400, detail="用户名或邮箱已存在")
    token = create_access_token({"user_id": user.id, "username": user.username})
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, data)
    if user is None:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    token = create_access_token({"user_id": user.id, "username": user.username})
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(require_auth)):
    return UserOut.model_validate(current_user)


@router.put("/profile", response_model=UserOut)
def update_profile(data: ProfileUpdate, current_user: User = Depends(require_auth), db: Session = Depends(get_db)):
    if data.nickname is not None:
        current_user.nickname = data.nickname
    if data.avatar_url is not None:
        current_user.avatar_url = data.avatar_url
    db.commit()
    db.refresh(current_user)
    return UserOut.model_validate(current_user)


@router.put("/password")
def change_password(data: PasswordChange, current_user: User = Depends(require_auth), db: Session = Depends(get_db)):
    if not verify_password(data.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="原密码错误")
    if len(data.new_password) < 6:
        raise HTTPException(status_code=400, detail="新密码至少6位")
    current_user.password_hash = hash_password(data.new_password)
    db.commit()
    return {"message": "密码修改成功"}


@router.get("/stats", response_model=UserStats)
def get_user_stats(current_user: User = Depends(require_auth), db: Session = Depends(get_db)):
    comment_count = db.query(func.count(Comment.id)).filter(Comment.user_id == current_user.id).scalar() or 0
    favorite_count = db.query(func.count(UserFavorite.id)).filter(UserFavorite.user_id == current_user.id).scalar() or 0
    member_days = (datetime.now() - current_user.created_at).days
    return UserStats(comment_count=comment_count, favorite_count=favorite_count, member_days=member_days)
