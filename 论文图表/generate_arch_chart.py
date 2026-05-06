"""
简洁版系统功能架构图 — 适合论文单栏插入
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import os

matplotlib.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False

BG = "#FAFAFA"
TEXT = "#1e293b"

LAYERS = [
    ("表现层", "#f472b6", "#fdf2f8", ["Vue 3 + Element Plus + ECharts\nHash 路由 SPA"]),
    ("业务层", "#3b82f6", "#eff6ff", [
        "用户管理 | 注册登录 / 个人中心",
        "视频浏览 | 搜索筛选 / 排序分页",
        "用户互动 | 评论回复 / 收藏管理",
        "数据分析 | 数据看板 / 可视化大屏",
    ]),
    ("服务层", "#8b5cf6", "#f5f3ff", ["FastAPI 路由模块 | JWT 认证中间件"]),
    ("数据层", "#10b981", "#ecfdf5", ["SQLAlchemy ORM | SQLite | Scrapy 爬虫"]),
]

fig, ax = plt.subplots(1, 1, figsize=(10, 5.5))
ax.set_xlim(0, 10)
ax.set_ylim(0, 5.5)
ax.axis("off")
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)


def box(ax, x, y, w, h, face, edge, text, tc, fs=9, bold=False, z=2):
    b = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06",
                       facecolor=face, edgecolor=edge, linewidth=1.2, zorder=z)
    ax.add_patch(b)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fs, fontweight="bold" if bold else "normal", color=tc, zorder=z + 1)


def arrow(ax, x1, y1, x2, y2, color="#cbd5e1"):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", color=color, lw=1.5), zorder=1)


layer_h = 1.05
layer_w = 9.0
layer_x = 0.5
gap = 0.15
start_y = 4.0

for i, (name, edge_c, face_c, items) in enumerate(LAYERS):
    y = start_y - i * (layer_h + gap)

    # Layer background
    b = FancyBboxPatch((layer_x, y), layer_w, layer_h, boxstyle="round,pad=0.06",
                       facecolor=face_c, edgecolor=edge_c, linewidth=1.5, zorder=1)
    ax.add_patch(b)

    # Layer label
    ax.text(layer_x + 0.15, y + layer_h / 2, name, ha="center", va="center",
            fontsize=7, fontweight="bold", color=edge_c, zorder=3)

    # Items
    n = len(items)
    item_w = (layer_w - 1.0) / n
    item_h = layer_h - 0.35
    for j, item_text in enumerate(items):
        ix = layer_x + 0.65 + j * item_w
        iy = y + 0.18
        box(ax, ix, iy, item_w - 0.1, item_h, "#ffffff", "#e2e8f0",
            item_text, TEXT, fs=7)

# Arrows between layers
for i in range(len(LAYERS) - 1):
    y_top = start_y - i * (layer_h + gap)
    y_bot = start_y - (i + 1) * (layer_h + gap) + layer_h
    ax.annotate("", xy=(9.6, y_bot), xytext=(9.6, y_top),
                arrowprops=dict(arrowstyle="->", color="#94a3b8", lw=1.2), zorder=1)

# Title
ax.text(5, 5.2, "系统功能架构图", ha="center", fontsize=13, fontweight="bold", color="#0f172a")

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chart9_系统功能架构图.png")
fig.savefig(out, dpi=250, bbox_inches="tight", facecolor=BG, edgecolor="none")
print(f"[OK] {out}  ({os.path.getsize(out)/1024:.0f} KB)")
plt.close(fig)
