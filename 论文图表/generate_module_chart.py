"""
简约版系统功能模块结构图 — 适合论文单栏插入
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

MODULES = [
    ("用户管理", ["注册 / 登录 / 个人中心"],
     "#3b82f6", "#eff6ff", "#1e40af"),
    ("视频浏览", ["搜索 / 筛选 / 排序 / 详情"],
     "#10b981", "#ecfdf5", "#065f46"),
    ("用户互动", ["评论回复 / 收藏管理"],
     "#f59e0b", "#fffbeb", "#92400e"),
    ("数据看板", ["多维统计 / 趋势分析"],
     "#8b5cf6", "#f5f3ff", "#5b21b6"),
    ("可视化大屏", ["全屏展示 / 实时数据"],
     "#06b6d4", "#ecfeff", "#0e7490"),
]

fig, ax = plt.subplots(1, 1, figsize=(10, 4.5))
ax.set_xlim(0, 10)
ax.set_ylim(0, 4.5)
ax.axis("off")
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)


def box(ax, x, y, w, h, face, edge, text, tc, fs=10, bold=False, z=2):
    b = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08",
                       facecolor=face, edgecolor=edge, linewidth=1.5, zorder=z)
    ax.add_patch(b)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fs, fontweight="bold" if bold else "normal", color=tc, zorder=z + 1)
    return b


def line(ax, x1, y1, x2, y2, color="#cbd5e1"):
    ax.plot([x1, x2], [y1, y2], color=color, linewidth=1.0, zorder=1)


# ── 根节点 ──
box(ax, 3.2, 3.6, 3.6, 0.5, "#fdf2f8", "#f472b6", "B站ACG视频数据分析系统", "#9d174d", fs=11, bold=True)

# ── 5 个子模块：单行排列 ──
positions = [(0.2, 1.8, 1.8), (2.2, 1.8, 1.8), (4.2, 1.8, 1.8),
             (6.2, 1.8, 1.8), (8.2, 1.8, 1.8)]

for i, ((name, children, edge_c, face_c, text_c), (lx, ly, lw)) in enumerate(zip(MODULES, positions)):
    lh = 1.2
    box(ax, lx, ly, lw, lh, face_c, edge_c, name, text_c, fs=9, bold=True)
    line(ax, 5.0, 3.6, lx + lw / 2, ly + lh, color=edge_c)

    n = len(children)
    cw = lw - 0.2
    for j, child_name in enumerate(children):
        cx = lx + 0.1
        cy = ly + 0.15
        box(ax, cx, cy, cw, lh - 0.9, "#f8fafc", "#e2e8f0", child_name, TEXT, fs=7)

# ── 标题 ──
ax.text(5, 4.2, "系统功能模块结构图", ha="center", fontsize=14, fontweight="bold", color="#0f172a")

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chart10_系统功能模块图.png")
fig.savefig(out, dpi=250, bbox_inches="tight", facecolor=BG, edgecolor="none")
print(f"[OK] {out}  ({os.path.getsize(out)/1024:.0f} KB)")
plt.close(fig)
