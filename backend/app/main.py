from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .routers import auth, videos, comments, dashboard, favorites
from .database import engine, Base, SessionLocal
from .config import get_settings
from .models.user import User
from .services.auth_service import hash_password

# Import all models so Base.metadata knows about them
from .models.user import User  # noqa: F401
from .models.video import Video, UserFavorite, VideoStatsHistory  # noqa: F401
from .models.comment import Comment  # noqa: F401

settings = get_settings()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="B站ACG视频数据统计分析系统",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(auth.router)
app.include_router(videos.router)
app.include_router(comments.router)
app.include_router(dashboard.router)
app.include_router(favorites.router)


def seed_default_users():
    db = SessionLocal()
    try:
        existing = db.query(User).first()
        if existing:
            return
        default_users = [
            ("admin", "admin123", "admin@acg.com", "\u7ba1\u7406\u5458"),
            ("user1", "user123", "user1@acg.com", "ACG\u7231\u597d\u8005"),
            ("user2", "user123", "user2@acg.com", "\u4e8c\u6b21\u5143\u840c\u65b0"),
        ]
        for username, pwd, email, nickname in default_users:
            user = User(
                username=username,
                password_hash=hash_password(pwd),
                email=email,
                nickname=nickname,
            )
            db.add(user)
        db.commit()
        print("Default users created: admin/admin123, user1/user123, user2/user123")
    finally:
        db.close()


seed_default_users()


@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": f"{settings.APP_NAME} is running"}


# Serve static files (frontend)
import os
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")

@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """Serve the SPA - all non-API routes return index.html"""
    file_path = os.path.join(static_dir, full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    return FileResponse(os.path.join(static_dir, "index.html"))


@app.get("/")
async def root():
    return FileResponse(os.path.join(static_dir, "index.html"))
