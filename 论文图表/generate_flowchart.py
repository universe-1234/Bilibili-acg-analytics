"""
简约版系统功能流程图 — 紧凑布局，适合论文插入
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon
import os

matplotlib.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False

BG = "#FAFAFA"
BLUE = "#3b82f6"
GREEN = "#10b981"
PURPLE = "#8b5cf6"
CYAN = "#06b6d4"
ORANGE = "#f59e0b"
GRAY = "#64748b"
DARK = "#1e293b"
DECISION_C = "#fef3c7"
DECISION_E = "#f59e0b"

fig, ax = plt.subplots(1, 1, figsize=(16, 8))
ax.set_xlim(0, 16)
ax.set_ylim(0, 8)
ax.axis("off")
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)


def bx(x, y, w, h, text, color=BLUE, fs=9, bold=False):
    b = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                       facecolor=color + "14", edgecolor=color, linewidth=1.5, zorder=2)
    ax.add_patch(b)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fs, fontweight="bold" if bold else "normal", color=DARK, zorder=3)

def dm(x, y, w, h, text, fs=8.5):
    pts = [(x + w / 2, y + h), (x + w, y + h / 2), (x + w / 2, y), (x, y + h / 2)]
    ax.add_patch(Polygon(pts, facecolor=DECISION_C, edgecolor=DECISION_E, linewidth=1.5, zorder=2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=DARK, zorder=3)

def ar(x1, y1, x2, y2, label="", fs=7):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", color=GRAY, lw=1.3), zorder=1)
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mx, my + 0.08, label, fontsize=fs, color=GRAY, ha="center", va="bottom", zorder=3)

# ═══════════════════════════════════════════
#  布局：横向为主，两行
# ═══════════════════════════════════════════

# 第1行：登录 → 首页 → 详情
bx(0.3, 6.0, 1.6, 0.7, "用户访问", GREEN, bold=True)
ar(1.9, 6.35, 2.8, 6.35)
dm(2.8, 5.9, 1.5, 0.9, "已登录?")

# 登录分支
ar(2.8, 5.9, 2.8, 4.7, "否")
bx(2.1, 3.7, 1.5, 0.65, "登录/注册", GRAY, fs=8)
ar(2.85, 4.35, 2.85, 3.85)
ar(3.55, 6.35, 5.5, 6.35, "是")

# 首页
bx(5.5, 5.8, 2.2, 1.1, "系统首页\n视频列表 · 搜索 · 筛选 · 排序", BLUE, bold=True, fs=9)

# 搜索回环
ar(7.7, 6.9, 8.5, 7.3, "")
ar(8.5, 7.3, 7.2, 7.3, "")
ar(6.6, 6.9, 6.6, 7.8, "")
bx(5.7, 7.8, 1.8, 0.55, "搜索结果刷新", BLUE, fs=7.5)

# 首页 → 详情
ar(7.7, 6.35, 9.2, 6.35, "")

# 详情
bx(9.2, 5.7, 2.0, 1.3, "视频详情页\n封面 · 数据 · 标签\nB站原视频链接", PURPLE, bold=True, fs=8.5)

# 详情 → 互动
ar(10.2, 5.7, 10.2, 4.7, "")
bx(9.2, 3.9, 2.0, 0.55, "收藏 / 取消收藏", ORANGE, fs=8)
bx(9.2, 3.2, 2.0, 0.55, "评论 / 回复", ORANGE, fs=8)

# ── 第2行：三大页面（从首页导航） ──
ar(6.6, 5.8, 6.6, 1.8, "")

dm(5.8, 1.0, 1.6, 0.7, "导航页?")
ar(6.6, 1.7, 6.6, 1.1)

# 三列
bx(0.3, 0.2, 3.0, 1.0, "数据看板 Dashboard\n概览 · 互动率 · 排行 · 趋势 · 标签云", PURPLE, bold=True, fs=8)
bx(4.8, 0.2, 3.0, 1.0, "可视化大屏 Big Screen\nKPI · 玫瑰图 · 雷达图 · 全屏 · 时钟", CYAN, bold=True, fs=8)
bx(9.3, 0.2, 3.0, 1.0, "个人中心 Profile\n头像 · 昵称 · 密码 · 个人统计", GREEN, bold=True, fs=8)

ar(6.6, 1.0, 1.8, 1.0, "")
ar(6.6, 1.0, 6.3, 1.0, "")
ar(6.6, 1.0, 10.8, 1.0, "")

# ── 退出分支 ──
dm(12.8, 0.85, 1.4, 0.8, "退出?")
ar(12.3, 0.7, 12.8 + 0.7, 1.25, "")
ar(12.8, 0.85, 12.8, -0.2, "是")
ar(13.5, 1.25, 14.3, 1.25, "否")
bx(14.3, 0.85, 1.5, 0.8, "返回首页", BLUE, fs=8)
ar(12.8 + 0.7, -0.2, 12.8 + 0.7, -0.8, "")
bx(12.1, -1.2, 1.8, 0.65, "清除令牌\n返回登录页", GRAY, fs=8)

# ═══════════════════════════════════════════
ax.text(8, 7.8, "B站ACG视频数据统计分析系统 — 系统功能流程图",
        ha="center", fontsize=14, fontweight="bold", color="#0f172a")

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chart11_系统功能流程图.png")
fig.savefig(out, dpi=250, bbox_inches="tight", facecolor=BG, edgecolor="none")
print(f"[OK] {out}")
plt.close(fig)
