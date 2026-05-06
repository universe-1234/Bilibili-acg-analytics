"""
生成论文风格的 E-R 图 — 矩形(实体) + 椭圆(属性) + 菱形(联系)
传统 Chen 记法，适合本科论文
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Ellipse, Polygon, FancyArrowPatch, Arc
import numpy as np
import os

matplotlib.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False

BG = "#FFFFFF"
ENTITY_COLOR = "#1e40af"
ENTITY_FACE = "#eff6ff"
ATTR_COLOR = "#374151"
ATTR_FACE = "#f9fafb"
REL_COLOR = "#9d174d"
REL_FACE = "#fdf2f8"
PK_COLOR = "#dc2626"
LINE_COLOR = "#6b7280"
TEXT_COLOR = "#1f2937"
CARD_COLOR = "#059669"

fig, ax = plt.subplots(1, 1, figsize=(18, 13))
ax.set_xlim(0, 18)
ax.set_ylim(0, 13)
ax.axis("off")
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)


def rect(ax, x, y, w, h, text, fs=9):
    """实体矩形"""
    b = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05",
                       facecolor=ENTITY_FACE, edgecolor=ENTITY_COLOR, linewidth=2, zorder=3)
    ax.add_patch(b)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fs, fontweight="bold", color=ENTITY_COLOR, zorder=4)


def ellipse(ax, x, y, w, h, text, fs=7, pk=False):
    """属性椭圆"""
    e = Ellipse((x + w / 2, y + h / 2), w, h,
                facecolor=ATTR_FACE, edgecolor=ATTR_COLOR, linewidth=1, zorder=3)
    ax.add_patch(e)
    style = "normal"
    color = PK_COLOR if pk else TEXT_COLOR
    if pk:
        text = text  # 主键加下划线通过 \underline 在 mathtext 中实现
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fs, color=color, zorder=4)


def diamond(ax, x, y, w, h, text, fs=7):
    """联系菱形"""
    cx, cy = x + w / 2, y + h / 2
    pts = [(cx, cy - h / 2), (cx + w / 2, cy), (cx, cy + h / 2), (cx - w / 2, cy)]
    p = Polygon(pts, facecolor=REL_FACE, edgecolor=REL_COLOR, linewidth=1.5, zorder=3)
    ax.add_patch(p)
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fs, fontweight="bold",
            color=REL_COLOR, zorder=4)


def line(ax, x1, y1, x2, y2, lw=1, ls="-", color=LINE_COLOR):
    ax.plot([x1, x2], [y1, y2], color=color, linewidth=lw, linestyle=ls, zorder=1)


def label(ax, x, y, text, color=CARD_COLOR, fs=7):
    """基数标注 1/N/M"""
    ax.text(x, y, text, fontsize=fs, color=color, ha="center", va="center",
            fontweight="bold", zorder=5,
            bbox=dict(boxstyle="round,pad=0.1", facecolor="white", edgecolor="none", alpha=0.8))


def pk_mark(ax, x, y, w):
    """主键下划线"""
    ax.plot([x + 2, x + w - 2], [y - 2, y - 2], color=PK_COLOR, linewidth=1.5, zorder=4)


# ═══════════════════════════════════════════
#  实体位置
# ═══════════════════════════════════════════
# users 左上, videos 中上, comments 右上
# user_favorites 左下, video_stats_history 右下

ew, eh = 2.0, 1.0  # 实体尺寸
aw, ah = 1.4, 0.55  # 属性椭圆尺寸
dw, dh = 1.2, 0.65   # 菱形尺寸

# ─── 用户实体 ───
ux, uy = 0.8, 9.5
rect(ax, ux, uy, ew, eh, "用户 users")

# 用户属性 (左侧和上方)
uattrs = [
    (ux - 1.6, uy + 1.8, "用户ID", True),
    (ux - 1.6, uy + 1.0, "用户名"),
    (ux - 1.6, uy + 0.2, "密码哈希"),
    (ux + ew + 0.6, uy + 1.8, "邮箱"),
    (ux + ew + 0.6, uy + 1.0, "昵称"),
    (ux + ew + 0.6, uy + 0.2, "头像URL"),
]
for axx, ayy, txt, *pk in uattrs:
    is_pk = pk[0] if pk else False
    ellipse(ax, axx, ayy, aw, ah, txt, pk=is_pk)
    # 连线到实体
    cx_e = ux + ew / 2
    cy_e = uy + eh / 2
    cx_a = axx + aw / 2
    cy_a = ayy + ah / 2
    line(ax, cx_a, cy_a - ah / 2, cx_e, uy + eh if ayy > uy else uy)

# ─── 视频实体 ──
vx, vy = 7.0, 9.5
rect(ax, vx, vy, ew, eh, "视频 videos")

vattrs = [
    (vx - 1.8, vy + 2.2, "视频ID", True),
    (vx - 1.8, vy + 1.4, "BV号"),
    (vx - 3.0, vy + 0.4, "标题"),
    (vx + ew + 0.6, vy + 2.2, "播放量"),
    (vx + ew + 0.6, vy + 1.4, "点赞数"),
    (vx + ew + 0.6, vy + 0.6, "弹幕数"),
    (vx + ew + 2.6, vy + 2.2, "分类"),
    (vx + ew + 2.6, vy + 1.4, "UP主"),
    (vx + ew + 2.6, vy + 0.6, "时长"),
]
for axx, ayy, txt, *pk in vattrs:
    is_pk = pk[0] if pk else False
    ellipse(ax, axx, ayy, aw, ah, txt, pk=is_pk)
    cx_e = vx + ew / 2
    cy_e = vy + eh / 2
    cx_a = axx + aw / 2
    cy_a = ayy + ah / 2
    # Connect from attribute edge to entity
    if axx > vx + ew:
        line(ax, cx_a - aw / 2, cy_a, vx + ew, cy_e)
    elif axx < vx:
        line(ax, cx_a + aw / 2, cy_a, vx, cy_e)
    else:
        line(ax, cx_a, cy_a - ah / 2, cx_e, vy + eh)

# ─── 评论实体 ──
cx, cy = 14.0, 9.5
rect(ax, cx, cy, ew, eh, "评论 comments")

cattrs = [
    (cx - 1.8, cy + 1.6, "评论ID", True),
    (cx - 1.8, cy + 0.8, "评论内容"),
    (cx + ew + 0.6, cy + 1.6, "用户ID(FK)"),
    (cx + ew + 0.6, cy + 0.8, "视频ID(FK)"),
    (cx + ew + 0.6, cy + 0.0, "父评论ID(FK)"),
]
for axx, ayy, txt, *pk in cattrs:
    is_pk = pk[0] if pk else False
    ellipse(ax, axx, ayy, aw, ah, txt, pk=is_pk)
    cx_e = cx + ew / 2
    cy_e = cy + eh / 2
    cx_a = axx + aw / 2
    cy_a = ayy + ah / 2
    if axx > cx + ew:
        line(ax, cx_a - aw / 2, cy_a, cx + ew, cy_e)
    else:
        line(ax, cx_a + aw / 2, cy_a, cx, cy_e)

# ─── 收藏实体 ──
fx, fy = 2.0, 4.5
rect(ax, fx, fy, ew, eh, "用户收藏\nuser_favorites")

fattrs = [
    (fx - 1.8, fy + 1.6, "收藏ID", True),
    (fx - 1.8, fy + 0.8, "用户ID(FK)"),
    (fx + ew + 0.6, fy + 1.6, "视频ID(FK)"),
    (fx + ew + 0.6, fy + 0.8, "收藏时间"),
]
for axx, ayy, txt, *pk in fattrs:
    is_pk = pk[0] if pk else False
    ellipse(ax, axx, ayy, aw, ah, txt, pk=is_pk)
    cx_e = fx + ew / 2
    cy_e = fy + eh / 2
    cx_a = axx + aw / 2
    cy_a = ayy + ah / 2
    if axx > fx + ew:
        line(ax, cx_a - aw / 2, cy_a, fx + ew, cy_e)
    else:
        line(ax, cx_a + aw / 2, cy_a, fx, cy_e)

# ─── 历史统计实体 ──
hx, hy = 10.0, 4.5
rect(ax, hx, hy, ew, eh, "历史统计\nvideo_stats_history")

hattrs = [
    (hx - 1.8, hy + 2.2, "记录ID", True),
    (hx - 1.8, hy + 1.4, "视频ID(FK)"),
    (hx - 1.8, hy + 0.4, "记录时间"),
    (hx + ew + 0.6, hy + 2.2, "播放量快照"),
    (hx + ew + 0.6, hy + 1.4, "点赞数快照"),
    (hx + ew + 0.6, hy + 0.6, "弹幕数快照"),
]
for axx, ayy, txt, *pk in hattrs:
    is_pk = pk[0] if pk else False
    ellipse(ax, axx, ayy, aw, ah, txt, pk=is_pk)
    cx_e = hx + ew / 2
    cy_e = hy + eh / 2
    cx_a = axx + aw / 2
    cy_a = ayy + ah / 2
    if axx > hx + ew:
        line(ax, cx_a - aw / 2, cy_a, hx + ew, cy_e)
    else:
        line(ax, cx_a + aw / 2, cy_a, hx, cy_e)

# ═══════════════════════════════════════════
#  联系 (菱形)
# ═══════════════════════════════════════════

# 用户 ←→ 评论: 1:N 发表
r1x, r1y = ux + ew + 1.8, uy - 1.0
diamond(ax, r1x, r1y, dw, dh, "发表")
line(ax, ux + ew, uy + eh / 2, r1x + dw / 2, r1y + dh / 2)
line(ax, r1x + dw / 2, r1y + dh / 2, cx, cy + eh / 2)
label(ax, ux + ew + 0.5, uy + eh / 2 - 0.1, "1")
label(ax, cx - 0.4, cy + eh / 2 - 0.1, "N")

# 用户 ←→ 收藏: 1:N 收藏
r2x, r2y = ux + ew + 0.5, uy - 4.5
diamond(ax, r2x, r2y, dw, dh, "收藏")
line(ax, ux + ew / 2, uy, r2x + dw / 2, r2y + dh / 2)
line(ax, r2x + dw / 2, r2y + dh / 2, fx + ew / 2, fy + eh)
label(ax, ux + ew / 2 + 0.3, uy - 0.5, "1")
label(ax, fx + ew / 2 + 0.3, fy + eh - 0.1, "N")

# 视频 ←→ 评论: 1:N 包含
r3x, r3y = vx + ew + 2.0, uy - 1.0
diamond(ax, r3x, r3y, dw, dh, "包含")
line(ax, vx + ew, vy + eh / 2, r3x + dw / 2, r3y + dh / 2)
line(ax, r3x + dw / 2, r3y + dh / 2, cx, cy + eh / 2)
label(ax, vx + ew + 0.8, vy + eh / 2 - 0.1, "1")
label(ax, cx - 0.4, cy + eh / 2 - 0.1, "N")

# 视频 ←→ 收藏: 1:N 被收藏
r4x, r4y = vx - 1.8, vy - 4.5
diamond(ax, r4x, r4y, dw, dh, "被收藏")
line(ax, vx + ew / 2, vy, r4x + dw / 2, r4y + dh / 2)
line(ax, r4x + dw / 2, r4y + dh / 2, fx + ew / 2, fy + eh)
label(ax, vx + ew / 2 - 0.3, vy - 0.5, "1")
label(ax, fx + ew / 2 - 0.3, fy + eh - 0.1, "N")

# 视频 ←→ 历史: 1:N 记录
r5x, r5y = vx + ew + 2.0, vy - 4.5
diamond(ax, r5x, r5y, dw, dh, "历史记录")
line(ax, vx + ew, vy + eh / 2, r5x + dw / 2, r5y + dh / 2)
line(ax, r5x + dw / 2, r5y + dh / 2, hx + ew / 2, hy + eh)
label(ax, vx + ew + 0.8, vy + eh / 2 + 0.1, "1")
label(ax, hx + ew / 2 + 0.3, hy + eh - 0.1, "N")

# 评论 ←→ 评论: 1:N 回复 (自引用)
r6x, r6y = cx - 2.0, cy - 1.0
diamond(ax, r6x, r6y, dw, dh, "回复")
line(ax, cx, cy + eh / 2, r6x + dw / 2, r6y + dh / 2)
# 回环到自己
line(ax, r6x + dw / 2, r6y + dh / 2, cx - 0.5, cy - 0.3)
label(ax, cx - 0.8, cy + eh / 2 - 0.1, "1")
label(ax, cx - 0.8, cy - 0.5, "N")

# ═══════════════════════════════════════════
#  图例 + 标题
# ═══════════════════════════════════════════
# 图例
legend_y = 0.3
rect(ax, 0.5, legend_y, 1.4, 0.5, "实体", fs=7)
ellipse(ax, 2.3, legend_y, 1.4, 0.5, "属性", fs=7)
diamond(ax, 4.1, legend_y, 1.2, 0.5, "联系", fs=6)
ax.text(5.6, legend_y + 0.25, "—— 主键 (下划线标识)", fontsize=7, color=PK_COLOR, va="center")
ax.text(5.6, legend_y - 0.05, "1 / N  基数约束", fontsize=7, color=CARD_COLOR, va="center")

# 主键图例标记
ax.plot([9.1, 10.1], [legend_y + 0.15, legend_y + 0.15], color=PK_COLOR, linewidth=1.5)

ax.text(9, 12.5, "B站ACG视频数据统计分析系统 — 数据库 E-R 图",
        ha="center", fontsize=16, fontweight="bold", color="#0f172a")

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chart12_数据库ER图.png")
fig.savefig(out, dpi=250, bbox_inches="tight", facecolor=BG, edgecolor="none")
print(f"[OK] {out}  ({os.path.getsize(out)/1024:.0f} KB)")
plt.close(fig)
