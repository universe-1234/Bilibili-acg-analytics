"""
Mock data generator for demo / testing.
Generates 800+ ACG videos, random comments, and sample users.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import random
import hashlib
from datetime import datetime, timedelta
from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.video import Video, UserFavorite, VideoStatsHistory
from app.models.comment import Comment
from app.services.auth_service import hash_password

Base.metadata.create_all(bind=engine)

CATEGORIES = ["动画", "漫画", "游戏", "轻小说", "COSPLAY", "MAD·AMV", "MMD·3D", "手书", "特摄", "VOCALOID"]
TAGS_POOL = [
    "热血", "治愈", "搞笑", "恋爱", "战斗", "奇幻", "科幻", "日常", "校园", "异世界",
    "悬疑", "冒险", "美食", "音乐", "运动", "励志", "机甲", "魔法", "妖怪", "侦探",
    "新番", "经典", "剧场版", "OVA", "国创", "日漫", "泡面番", "原创", "漫画改", "轻改",
]
AUTHORS = [
    ("哔哩哔哩番剧", "928123"), ("动画学术趴", "234567"), ("LexBurner", "777536"),
    ("凉风Kaze", "123456"), ("泛式", "332211"), ("瓶子君152", "445566"),
    ("呜喵", "998877"), ("动画魂-Anitama", "556677"), ("木鱼水心", "112233"),
    ("动画纪", "667788"),
]
TITLES_TEMPLATE = [
    "【{year}年{month}月新番】{title} PV第{pv}弹",
    "【MAD】{title} × {song} 燃向混剪",
    "{title} 第{ep}话 剧情深度解析",
    "【{category}推荐】{title} 值得一看的佳作",
    "{title} 名场面合集 | {character}高光时刻",
    "【杂谈】为什么{title}是{year}年最好的{category}作品",
    "{title} 动画原声带 - {song}",
    "【MMD】{character} {dance} 60fps",
    "【手书】{title} {character}同人创作",
    "{title} 最终话reaction | 泪目了",
]
ANIME_TITLES = [
    "咒术回战", "鬼灭之刃", "间谍过家家", "葬送的芙莉莲", "药屋少女的呢喃",
    "迷宫饭", "我推的孩子", "进击的巨人", "电锯人", "孤独摇滚",
    "铃芽之旅", "想要成为影之实力者", "无职转生", "Re:从零开始的异世界生活",
    "关于我转生变成史莱姆这档事", "OVERLORD", "某科学的超电磁炮", "刀剑神域",
    "夏目友人帐", "钢之炼金术师", "命运石之门", "CLANNAD", "紫罗兰永恒花园",
    "冰菓", "吹响吧上低音号", "莉可丽丝", "Lycoris Recoil", "GRIDMAN",
    "SSSS.DYNAZENON", "古利特", "86-不存在的战区", "辉夜大小姐想让我告白",
    "更衣人偶坠入爱河", "式守同学不只可爱而已", "夏日重现", "朋友游戏",
    "地狱乐", "天国大魔境", "物理魔法使马修", "我心里危险的东西",
    "跃动青春", "和山田进行LV.999的恋爱", "真正 companions 是勇者",
]
SONGS = ["残酷な天使のテーゼ", "idol", "紅蓮華", "炎", "廻廻奇譚", "KICK BACK", "祝福"]
CHARACTERS = ["五条悟", "炭治郎", "阿尼亚", "芙莉莲", "星野爱", "艾伦", "波奇塔"]
DANCES = ["极乐净土", "恋爱循环", "drop pop candy", "威風堂々"]


def generate_bv_id():
    chars = "1pP2QoO3Rr4Ss5Tt6Uu7Vv8Ww9XxYyZzaABbCcDdEeFfGgHhIiJjKkLlMmNn"
    return "BV" + "".join(random.choices(chars, k=10))


def generate_title():
    template = random.choice(TITLES_TEMPLATE)
    anime = random.choice(ANIME_TITLES)
    song = random.choice(SONGS)
    character = random.choice(CHARACTERS)
    dance = random.choice(DANCES)
    category = random.choice(CATEGORIES[:5])
    return template.format(
        year=random.randint(2020, 2025),
        month=random.randint(1, 12),
        title=anime,
        pv=random.randint(1, 5),
        song=song,
        ep=random.randint(1, 24),
        category=category,
        character=character,
        dance=dance,
    )


def generate_videos(count=800):
    db = SessionLocal()
    try:
        for i in range(count):
            bv_id = generate_bv_id()
            title = generate_title()
            category = random.choice(CATEGORIES)
            tags = ",".join(random.sample(TAGS_POOL, random.randint(3, 7)))
            days_ago = random.randint(1, 365)
            publish_date = datetime.now() - timedelta(days=days_ago)

            # Power-law distribution: top videos get ~10M views, most get 1000-50000
            # This creates dramatic differentiation so charts look realistic
            rank_factor = random.random() ** 3  # Cube to make extreme skew
            play_count = int(1000 + rank_factor * (10000000 - 1000))
            like_count = int(play_count * random.uniform(0.02, 0.08))
            danmaku_count = int(play_count * random.uniform(0.005, 0.03))
            coin_count = int(play_count * random.uniform(0.002, 0.015))
            favorite_count = int(play_count * random.uniform(0.01, 0.06))
            share_count = int(play_count * random.uniform(0.001, 0.01))
            reply_count = int(play_count * random.uniform(0.001, 0.005))

            duration = f"{random.randint(0, 30):02d}:{random.randint(0, 59):02d}"
            if random.random() < 0.1:
                duration = f"{random.randint(1, 2):02d}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}"

            author_name, author_id = random.choice(AUTHORS)

            video = Video(
                bv_id=bv_id,
                title=title,
                description=f"这是一部关于{title}的精彩视频，由{author_name}创作，收录于{category}分类。标签包含：{tags}。",
                cover_url=f"https://picsum.photos/seed/{bv_id}/480/300",
                play_count=play_count,
                danmaku_count=danmaku_count,
                like_count=like_count,
                coin_count=coin_count,
                favorite_count=favorite_count,
                share_count=share_count,
                reply_count=reply_count,
                duration=duration,
                author_name=author_name,
                author_id=author_id,
                category=category,
                tags=tags,
                publish_date=publish_date,
                bilibili_url=f"https://www.bilibili.com/video/{bv_id}",
            )
            db.add(video)
            if (i + 1) % 100 == 0:
                db.commit()
                print(f"Created {i + 1} videos...")
        db.commit()
        print(f"Total videos created: {count}")
    finally:
        db.close()


def generate_users():
    db = SessionLocal()
    try:
        default_users = [
            ("admin", "admin123", "admin@acg.com", "管理员"),
            ("user1", "user123", "user1@acg.com", "ACG爱好者"),
            ("user2", "user123", "user2@acg.com", "二次元萌新"),
            ("user3", "user123", "user3@acg.com", "动漫达人"),
            ("user4", "user123", "user4@acg.com", "游戏玩家"),
        ]
        for username, pwd, email, nickname in default_users:
            existing = db.query(User).filter(User.username == username).first()
            if not existing:
                user = User(
                    username=username,
                    password_hash=hash_password(pwd),
                    email=email,
                    nickname=nickname,
                )
                db.add(user)
        db.commit()
        print("Users created!")
    finally:
        db.close()


def generate_comments(count=2000):
    db = SessionLocal()
    try:
        users = db.query(User).all()
        videos = db.query(Video).all()
        if not users or not videos:
            print("Need users and videos first!")
            return

        comments = [
            "这部作品真的太棒了！画风和剧情都是一流水准。",
            "每周都在等更新，这是我最喜欢的新番之一。",
            "UP主分析得很有深度，让我对这部作品有了新的理解。",
            "BGM配得太好了，燃哭了！",
            "这个名场面我反复看了十遍，每次都被感动到。",
            "声优的演技太强了，完全代入角色。",
            "制作组真的很用心，细节满分。",
            "这部作品的音乐监修实在是太厉害了。",
            "动画改编比原作还精彩，很少有这种情况。",
            "推荐给所有ACG爱好者，绝对不能错过！",
            "期待下一季！动画组加油！",
            "这画质，这帧数，经费在燃烧啊！",
            "看完之后马上去补了原作，真的赞。",
            "节奏把控得太好了，一点不拖沓。",
            "弹幕全是名场面打卡，笑死我了。",
            "这个转场设计太精妙了，导演功力深厚。",
            "每一帧都可以当壁纸的程度！",
            "第一次看的时候完全被震撼到了。",
            "好的作品值得反复品味。",
            "希望能有更多人看到这部优秀的作品。",
            "UP主的解说让我注意到了很多以前没发现的细节。",
            "这剪辑，这转场，UP主是专业的吧？",
            "已经收藏了，以后还会回来看。",
            "制作组的用心程度真的让人感动。",
            "这部作品改变了我对动画的认知。",
            "每一个角色都塑造得很立体。",
            "世界观设定很新颖，让人眼前一亮。",
            "这是我今年的年度最佳！",
            "剧情反转太出乎意料了，编剧是天才。",
            "希望能出第二季，等不及了！",
        ]

        for i in range(count):
            user = random.choice(users)
            video = random.choice(videos)
            content = random.choice(comments)
            comment = Comment(
                user_id=user.id,
                video_id=video.id,
                content=content,
            )
            db.add(comment)
            if (i + 1) % 500 == 0:
                db.commit()
                print(f"Created {i + 1} comments...")
        db.commit()
        print(f"Total comments created: {count}")
    finally:
        db.close()


def generate_stats_history(days=30):
    db = SessionLocal()
    try:
        videos = db.query(Video).all()
        if not videos:
            print("Need videos first!")
            return
        count = 0
        for i in range(days):
            date = datetime.now() - timedelta(days=days - i)
            for video in random.sample(videos, min(50, len(videos))):
                variation = random.uniform(0.9, 1.15)
                stat = VideoStatsHistory(
                    video_id=video.id,
                    play_count=int(video.play_count * variation),
                    danmaku_count=int(video.danmaku_count * variation),
                    like_count=int(video.like_count * variation),
                    favorite_count=int(video.favorite_count * variation),
                    recorded_at=date + timedelta(hours=random.randint(0, 23)),
                )
                db.add(stat)
                count += 1
                if count % 500 == 0:
                    db.commit()
        db.commit()
        print(f"Total stats history created: {count}")
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--videos", type=int, default=800)
    parser.add_argument("--comments", type=int, default=2000)
    parser.add_argument("--history-days", type=int, default=30)
    args = parser.parse_args()

    print("=== Generating Users ===")
    generate_users()

    print("\n=== Generating Videos ===")
    generate_videos(args.videos)

    print("\n=== Generating Comments ===")
    generate_comments(args.comments)

    print("\n=== Generating Stats History ===")
    generate_stats_history(args.history_days)

    print("\n=== All Done! ===")
