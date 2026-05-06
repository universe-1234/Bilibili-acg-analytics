"""
论文图表生成脚本
使用 matplotlib 从真实数据库生成论文可用的高清图表。
运行: cd C:\Cc_code\bilibili-acg-analytics && python 论文图表\generate_thesis_charts.py
"""

import sys
import os

# 确保能找到 backend 模块
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from collections import Counter
from sqlalchemy import func, desc

# ---------- 中文字体配置 ----------
matplotlib.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False


def get_data():
    """连接数据库并返回常用查询结果"""
    from app.database import SessionLocal
    from app.models.video import Video, UserFavorite
    from app.models.comment import Comment
    from app.models.user import User
    from app.routers.dashboard import parse_duration

    session = SessionLocal()

    # 概览
    total_videos = session.query(func.count(Video.id)).scalar() or 0
    total_comments = session.query(func.count(Comment.id)).scalar() or 0
    total_users = session.query(func.count(User.id)).scalar() or 0
    total_plays = session.query(func.sum(Video.play_count)).scalar() or 0
    total_likes = session.query(func.sum(Video.like_count)).scalar() or 0
    total_danmaku = session.query(func.sum(Video.danmaku_count)).scalar() or 0

    overview = {
        "videos": total_videos,
        "comments": total_comments,
        "users": total_users,
        "plays": total_plays,
        "likes": total_likes,
        "danmaku": total_danmaku,
    }

    # 分类统计
    category_rows = (
        session.query(
            Video.category,
            func.count(Video.id).label("count"),
            func.sum(Video.play_count).label("plays"),
        )
        .filter(Video.category != "")
        .group_by(Video.category)
        .order_by(desc(func.sum(Video.play_count)))
        .all()
    )
    categories = [r[0] for r in category_rows]
    cat_counts = [r[1] for r in category_rows]
    cat_plays = [r[2] or 0 for r in category_rows]

    # Top 视频
    top_videos = (
        session.query(Video)
        .order_by(desc(Video.play_count))
        .limit(15)
        .all()
    )

    # 每日趋势
    from app.models.video import VideoStatsHistory
    daily = (
        session.query(
            func.date(VideoStatsHistory.recorded_at).label("date"),
            func.sum(VideoStatsHistory.play_count).label("plays"),
        )
        .group_by("date")
        .order_by("date")
        .limit(30)
        .all()
    )

    # 标签云
    tag_rows = session.query(Video.tags).filter(Video.tags != "").all()
    tag_counter = Counter()
    for (tags_str,) in tag_rows:
        for tag in tags_str.split(","):
            t = tag.strip()
            if t:
                tag_counter[t] += 1
    top_tags = tag_counter.most_common(15)

    # UP主排行
    author_rows = (
        session.query(
            Video.author_name,
            func.count(Video.id).label("count"),
            func.sum(Video.play_count).label("plays"),
        )
        .filter(Video.author_name != "")
        .group_by(Video.author_name)
        .order_by(desc(func.sum(Video.play_count)))
        .limit(10)
        .all()
    )

    # 互动率分析（分类维度）
    engage_rows = (
        session.query(
            Video.category,
            func.sum(Video.play_count).label("plays"),
            func.sum(Video.like_count).label("likes"),
            func.sum(Video.danmaku_count).label("danmaku"),
            func.sum(Video.coin_count).label("coins"),
            func.sum(Video.favorite_count).label("favs"),
            func.sum(Video.share_count).label("shares"),
        )
        .filter(Video.category != "")
        .group_by(Video.category)
        .all()
    )

    def safe_rate(n, d):
        return round(n / d * 100, 2) if d and d > 0 else 0

    engage_data = []
    for r in engage_rows:
        if r[1] and r[1] > 0:
            engage_data.append({
                "category": r[0],
                "like_rate": safe_rate(r[2], r[1]),
                "danmaku_rate": safe_rate(r[3], r[1]),
                "coin_rate": safe_rate(r[4], r[1]),
                "fav_rate": safe_rate(r[5], r[1]),
                "share_rate": safe_rate(r[6], r[1]),
            })

    # 时长分析
    dur_rows = session.query(Video.duration, Video.play_count, Video.like_count).all()
    buckets = {"<1分钟": [], "1-3分钟": [], "3-10分钟": [], "10-30分钟": [], ">30分钟": []}
    for dur_str, plays, likes in dur_rows:
        secs = parse_duration(dur_str)
        if secs < 60:
            b = "<1分钟"
        elif secs < 180:
            b = "1-3分钟"
        elif secs < 600:
            b = "3-10分钟"
        elif secs < 1800:
            b = "10-30分钟"
        else:
            b = ">30分钟"
        buckets[b].append((plays or 0, likes or 0))

    dur_analysis = []
    for name in ["<1分钟", "1-3分钟", "3-10分钟", "10-30分钟", ">30分钟"]:
        items = buckets[name]
        if items:
            dur_analysis.append({
                "bucket": name,
                "count": len(items),
                "avg_plays": sum(p for p, _ in items) / len(items),
                "avg_likes": sum(l for _, l in items) / len(items),
            })

    session.close()
    return {
        "overview": overview,
        "categories": list(zip(categories, cat_counts, cat_plays)),
        "top_videos": [(v.title, v.play_count, v.like_count, v.danmaku_count) for v in top_videos],
        "daily": [(str(d[0]), d[1]) for d in daily],
        "tags": top_tags,
        "authors": [(r[0], r[1], r[2] or 0) for r in author_rows],
        "engage": engage_data,
        "duration": dur_analysis,
    }


def parse_duration(dur_str):
    if not dur_str:
        return 0
    parts = dur_str.strip().split(":")
    if len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    elif len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    return 0


# ─── 配色方案 ───
C_PINK = "#f472b6"
C_CYAN = "#00d4ff"
C_PURPLE = "#a78bfa"
C_GREEN = "#34d399"
C_GOLD = "#fbbf24"
C_RED = "#f87171"
C_BLUE = "#60a5fa"
C_ORANGE = "#fb923c"
DARK_BG = "#0f0f23"
DARK_FACE = "#1a1a2e"
LIGHT_TEXT = "#cccccc"
PALETTE = [C_CYAN, C_PINK, C_PURPLE, C_GREEN, C_GOLD, C_RED, C_BLUE, C_ORANGE,
           "#818cf8", "#2dd4bf", "#e879f9", "#4ade80"]


def fmt_big(n):
    """大数字格式化"""
    if n >= 1e8:
        return f"{n / 1e8:.1f}亿"
    if n >= 1e4:
        return f"{n / 1e4:.1f}万"
    return str(int(n))


def setup_style(fig, title, figsize=(14, 8)):
    """统一暗色主题风格"""
    fig.patch.set_facecolor(DARK_BG)
    ax = fig.add_subplot(111)
    ax.set_facecolor(DARK_FACE)
    ax.set_title(title, color="white", fontsize=18, fontweight="bold", pad=16)
    ax.tick_params(colors=LIGHT_TEXT, labelsize=10)
    for spine in ax.spines.values():
        spine.set_color("#333355")
    ax.xaxis.label.set_color(LIGHT_TEXT)
    ax.yaxis.label.set_color(LIGHT_TEXT)
    return ax


def save_fig(fig, name):
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=DARK_BG, edgecolor="none")
    print(f"  [OK] 已生成: {out}")
    plt.close(fig)


# ═══════════════════════════════════════════
#  图1: 分类视频数量分布 — 南丁格尔玫瑰图
# ═══════════════════════════════════════════
def chart1_pie(data):
    cats = [c for c, cnt, _ in data["categories"]]
    vals = [cnt for _, cnt, _ in data["categories"]]

    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, polar=True)
    fig.patch.set_facecolor(DARK_BG)
    ax.set_facecolor(DARK_FACE)
    ax.set_title("视频分类数量分布", color="white", fontsize=18, fontweight="bold", pad=24)

    n = len(vals)
    theta = np.linspace(0, 2 * np.pi, n, endpoint=False)
    width = 2 * np.pi / n * 0.85
    colors = [PALETTE[i % len(PALETTE)] for i in range(n)]

    bars = ax.bar(theta, vals, width=width, bottom=50, color=colors, alpha=0.9, edgecolor=DARK_BG, linewidth=0.5)
    ax.set_xticks(theta)
    ax.set_xticklabels(cats, color=LIGHT_TEXT, fontsize=10)
    ax.set_yticklabels([])
    ax.spines["polar"].set_color("#333355")
    ax.grid(color="#222244", alpha=0.3)

    # 标注数值
    for t, v in zip(theta, vals):
        ax.annotate(str(v), xy=(t, v + max(vals) * 0.08),
                    ha="center", va="bottom", color=LIGHT_TEXT, fontsize=8)

    save_fig(fig, "chart1_分类数量玫瑰图.png")


# ═══════════════════════════════════════════
#  图2: TOP15 视频播放量排行
# ═══════════════════════════════════════════
def chart2_top_videos(data):
    vids = data["top_videos"]
    titles = [v[0][:18] + "..." if len(v[0]) > 18 else v[0] for v in reversed(vids)]
    plays = [v[1] for v in reversed(vids)]

    fig = plt.figure(figsize=(14, 10))
    ax = setup_style(fig, "TOP15 热门视频播放量排行")
    y_pos = range(len(titles))
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(titles))]

    ax.barh(y_pos, plays, color=colors, height=0.7, alpha=0.9, edgecolor=DARK_BG)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(titles, fontsize=9)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: fmt_big(x)))

    for i, (p, title) in enumerate(zip(plays, titles)):
        ax.text(p + max(plays) * 0.01, i, fmt_big(p), va="center", color=LIGHT_TEXT, fontsize=8)

    ax.grid(axis="x", color="#222244", alpha=0.3)
    save_fig(fig, "chart2_TOP15播放量排行.png")


# ═══════════════════════════════════════════
#  图3: 30天数据趋势 — 折线图
# ═══════════════════════════════════════════
def chart3_trend(data):
    daily = data["daily"]
    if not daily:
        print("  [WARN] 无每日趋势数据，跳过")
        return
    dates = [d[0][5:] for d in daily]
    plays = [d[1] for d in daily]

    fig = plt.figure(figsize=(14, 7))
    ax = setup_style(fig, "视频数据 30天趋势")

    ax.plot(dates, plays, color=C_CYAN, linewidth=2.5, marker="o", markersize=4, markerfacecolor=C_CYAN, label="播放量")
    ax.fill_between(range(len(dates)), plays, alpha=0.15, color=C_CYAN)
    ax.legend(facecolor=DARK_FACE, edgecolor="#333355", labelcolor=LIGHT_TEXT, fontsize=10)
    ax.xaxis.set_major_locator(ticker.MaxNLocator(8))
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: fmt_big(x)))
    ax.tick_params(axis="x", rotation=30)
    ax.grid(color="#222244", alpha=0.3)

    save_fig(fig, "chart3_30天趋势图.png")


# ═══════════════════════════════════════════
#  图4: UP主影响力排行
# ═══════════════════════════════════════════
def chart4_authors(data):
    authors = data["authors"]
    names = [a[0] for a in reversed(authors)]
    plays = [a[2] for a in reversed(authors)]
    counts = [a[1] for a in reversed(authors)]

    fig = plt.figure(figsize=(14, 8))
    ax = setup_style(fig, "UP主影响力排行 Top10")

    y_pos = range(len(names))
    ax.barh(y_pos, plays, color=C_GOLD, height=0.6, alpha=0.85, edgecolor=DARK_BG, label="总播放量")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=10)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: fmt_big(x)))

    for i, (p, c) in enumerate(zip(plays, counts)):
        ax.text(p + max(plays) * 0.01, i, f"{fmt_big(p)}  ({c}视频)",
                va="center", color=LIGHT_TEXT, fontsize=8)

    ax.legend(facecolor=DARK_FACE, edgecolor="#333355", labelcolor=LIGHT_TEXT)
    ax.grid(axis="x", color="#222244", alpha=0.3)
    save_fig(fig, "chart4_UP主排行.png")


# ═══════════════════════════════════════════
#  图5: 热门标签云
# ═══════════════════════════════════════════
def chart5_tags(data):
    tags = data["tags"]
    names = [t[0] for t in reversed(tags)]
    vals = [t[1] for t in reversed(tags)]

    fig = plt.figure(figsize=(14, 8))
    ax = setup_style(fig, "热门标签 Top15")
    y_pos = range(len(names))
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(names))]

    ax.barh(y_pos, vals, color=colors, height=0.7, alpha=0.9, edgecolor=DARK_BG)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=10)
    for i, v in enumerate(vals):
        ax.text(v + max(vals) * 0.01, i, str(v), va="center", color=LIGHT_TEXT, fontsize=9)
    ax.grid(axis="x", color="#222244", alpha=0.3)
    save_fig(fig, "chart5_热门标签.png")


# ═══════════════════════════════════════════
#  图6: 分类互动率对比 — 分组柱状图
# ═══════════════════════════════════════════
def chart6_engagement(data):
    engage = data["engage"]
    if not engage:
        print("  [WARN] 无互动率数据，跳过")
        return

    categories = [e["category"] for e in engage[:8]]
    metrics = ["like_rate", "danmaku_rate", "coin_rate", "fav_rate", "share_rate"]
    labels = ["点赞率", "弹幕率", "投币率", "收藏率", "分享率"]
    colors = [C_PINK, C_CYAN, C_GOLD, C_GREEN, C_PURPLE]

    x = np.arange(len(categories))
    width = 0.15
    n = len(metrics)

    fig = plt.figure(figsize=(16, 8))
    ax = setup_style(fig, "各类别互动率对比分析", figsize=(16, 8))

    for i, (metric, label, color) in enumerate(zip(metrics, labels, colors)):
        vals = [e[metric] for e in engage[:8]]
        offset = (i - n / 2 + 0.5) * width
        ax.bar(x + offset, vals, width, label=label, color=color, alpha=0.85, edgecolor=DARK_BG)

    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=10)
    ax.legend(facecolor=DARK_FACE, edgecolor="#333355", labelcolor=LIGHT_TEXT, fontsize=9, ncol=5, loc="upper right")
    ax.set_ylabel("互动率 (%)", color=LIGHT_TEXT, fontsize=11)
    ax.grid(axis="y", color="#222244", alpha=0.3)
    save_fig(fig, "chart6_分类互动率对比.png")


# ═══════════════════════════════════════════
#  图7: 时长区间分析
# ═══════════════════════════════════════════
def chart7_duration(data):
    dur = data["duration"]
    if not dur:
        print("  [WARN] 无时长数据，跳过")
        return

    buckets = [d["bucket"] for d in dur]
    counts = [d["count"] for d in dur]
    avg_plays = [d["avg_plays"] for d in dur]

    fig = plt.figure(figsize=(14, 8))
    ax1 = setup_style(fig, "视频时长区间分析")

    x = np.arange(len(buckets))
    width = 0.35

    ax1.bar(x - width / 2, counts, width, color=C_PINK, alpha=0.85, label="视频数量", edgecolor=DARK_BG)
    ax1.set_ylabel("视频数量", color=LIGHT_TEXT, fontsize=11)
    ax1.set_xticks(x)
    ax1.set_xticklabels(buckets, fontsize=11)
    for i, c in enumerate(counts):
        ax1.text(i - width / 2, c + max(counts) * 0.02, str(c), ha="center", color=LIGHT_TEXT, fontsize=9)

    ax2 = ax1.twinx()
    ax2.bar(x + width / 2, avg_plays, width, color=C_CYAN, alpha=0.7, label="平均播放量", edgecolor=DARK_BG)
    ax2.set_ylabel("平均播放量", color=LIGHT_TEXT, fontsize=11)
    ax2.tick_params(colors=LIGHT_TEXT)
    ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: fmt_big(x)))

    # 合并图例
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, facecolor=DARK_FACE, edgecolor="#333355",
               labelcolor=LIGHT_TEXT, fontsize=10, loc="upper right")

    ax1.grid(axis="y", color="#222244", alpha=0.3)
    save_fig(fig, "chart7_时长区间分析.png")


# ═══════════════════════════════════════════
#  图8: 系统 KPI 概览 (用作论文的系统规模展示)
# ═══════════════════════════════════════════
def chart8_kpi(data):
    ov = data["overview"]

    fig, axes = plt.subplots(1, 4, figsize=(18, 5))
    fig.patch.set_facecolor(DARK_BG)

    items = [
        ("视频总数", ov["videos"], C_PINK, ""),
        ("用户总数", ov["users"], C_CYAN, ""),
        ("评论总数", ov["comments"], C_PURPLE, ""),
        ("总播放量", fmt_big(ov["plays"]), C_GREEN, "累计"),
    ]

    for ax, (label, value, color, subtitle) in zip(axes, items):
        ax.set_facecolor(DARK_FACE)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        ax.text(0.5, 0.55, str(value), ha="center", va="center", fontsize=32,
                fontweight="bold", color=color, transform=ax.transAxes)
        ax.text(0.5, 0.22, label, ha="center", va="center", fontsize=12,
                color=LIGHT_TEXT, transform=ax.transAxes)
        if subtitle:
            ax.text(0.5, 0.08, subtitle, ha="center", va="center", fontsize=9,
                    color="#666666", transform=ax.transAxes)
        for spine in ax.spines.values():
            spine.set_color("#333355")
            spine.set_linewidth(0.5)

    fig.suptitle("系统数据规模概览", color="white", fontsize=20, fontweight="bold", y=1.02)
    save_fig(fig, "chart8_系统KPI概览.png")


# ═══════════════════════════════════════════
#  main
# ═══════════════════════════════════════════
def main():
    print("=" * 60)
    print("  毕业论文图表生成器")
    print("=" * 60)

    print("\n[1/8] 连接数据库并加载数据...")
    data = get_data()
    print(f"  数据库包含: {data['overview']['videos']} 视频, "
          f"{data['overview']['users']} 用户, "
          f"{data['overview']['comments']} 评论")

    print("\n[2/8] 分类数量玫瑰图...")
    chart1_pie(data)

    print("\n[3/8] TOP15 视频排行...")
    chart2_top_videos(data)

    print("\n[4/8] 30天趋势图...")
    chart3_trend(data)

    print("\n[5/8] UP主影响力排行...")
    chart4_authors(data)

    print("\n[6/8] 热门标签...")
    chart5_tags(data)

    print("\n[7/8] 分类互动率对比...")
    chart6_engagement(data)

    print("\n[8/8] 时长区间分析...")
    chart7_duration(data)

    print("\n[extra] KPI概览...")
    chart8_kpi(data)

    print(f"\n{'=' * 60}")
    print(f"  全部图表已生成至: {os.path.dirname(os.path.abspath(__file__))}")
    print(f"  共生成 8 张论文插图 (200 DPI, 暗色主题)")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
