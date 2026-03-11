"""Slide: Feature hierarchy in deep CNNs — edges → textures → objects."""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

BG = "#1a1a2e"
FG = "white"

np.random.seed(42)

def gabor_patch(size=20, theta=0):
    """Synthetic Gabor-like edge detector patch."""
    x = np.linspace(-np.pi, np.pi, size)
    X, Y = np.meshgrid(x, x)
    Xr = X * np.cos(theta) + Y * np.sin(theta)
    return np.cos(2 * Xr) * np.exp(-(X**2 + Y**2) / 2)

def random_texture(size=20):
    """Random texture-like pattern."""
    t = np.zeros((size, size))
    for _ in range(8):
        cx, cy = np.random.randint(3, size-3, 2)
        r = np.random.randint(2, 5)
        Y, X = np.ogrid[:size, :size]
        t += np.exp(-((X-cx)**2 + (Y-cy)**2) / (2*r**2))
    return t / t.max()

def face_like(size=20):
    """Very rough face-like shape."""
    m = np.zeros((size, size))
    Y, X = np.ogrid[:size, :size]
    # head
    head = ((X - size/2)**2 + (Y - size/2)**2) < (size/2.5)**2
    m[head] = 0.5
    # eyes
    eye1 = ((X - size*0.35)**2 + (Y - size*0.38)**2) < (size/9)**2
    eye2 = ((X - size*0.65)**2 + (Y - size*0.38)**2) < (size/9)**2
    m[eye1] = 1.0
    m[eye2] = 1.0
    # mouth
    mouth_y = int(size * 0.65)
    m[mouth_y, int(size*0.35):int(size*0.65)] = 1.0
    return m

levels = [
    {
        "title": "Шар 1:\nПрості ознаки",
        "subtitle": "Краї та лінії",
        "color": "#2980b9",
        "patches": [gabor_patch(20, theta) for theta in [0, np.pi/4, np.pi/2, 3*np.pi/4]],
    },
    {
        "title": "Шар 2:\nСередні ознаки",
        "subtitle": "Текстури, контури",
        "color": "#8e44ad",
        "patches": [random_texture() for _ in range(4)],
    },
    {
        "title": "Шар 3:\nВисокорівневі ознаки",
        "subtitle": "Частини об'єктів",
        "color": "#117a65",
        "patches": [face_like() for _ in range(4)],
    },
]

fig = plt.figure(figsize=(15, 6), facecolor=BG)
col_ratios = [0.12] + [1.0] * len(levels)
gs = fig.add_gridspec(1, len(levels) + 1, width_ratios=col_ratios,
                      wspace=0.35, left=0.02, right=0.98)

# Left: legend
ax_leg = fig.add_subplot(gs[0])
ax_leg.axis("off")
ax_leg.set_facecolor(BG)

for l_idx, level in enumerate(levels):
    ax_col = fig.add_subplot(gs[l_idx + 1])
    ax_col.axis("off")
    ax_col.set_facecolor(BG)

    # Mini grid of 4 patches (2×2)
    inner_gs = gs[l_idx + 1].subgridspec(3, 2, hspace=0.25, wspace=0.15)

    # Title row
    ax_title = fig.add_subplot(inner_gs[0, :])
    ax_title.axis("off")
    ax_title.set_facecolor(BG)
    bg_rect = patches.FancyBboxPatch(
        (0.05, 0.05), 0.9, 0.85,
        boxstyle="round,pad=0.05",
        facecolor=level["color"], edgecolor="none", alpha=0.35,
        transform=ax_title.transAxes
    )
    ax_title.add_patch(bg_rect)
    ax_title.text(0.5, 0.55, level["title"], ha="center", va="center",
                  fontsize=12, color=FG, fontweight="bold",
                  transform=ax_title.transAxes, multialignment="center")
    ax_title.text(0.5, 0.1, level["subtitle"], ha="center", va="bottom",
                  fontsize=10, color="#aed6f1",
                  transform=ax_title.transAxes)

    # 4 patch thumbnails (2 rows × 2 cols)
    for p_idx, patch_data in enumerate(level["patches"]):
        r, c = p_idx // 2 + 1, p_idx % 2
        ax_p = fig.add_subplot(inner_gs[r, c])
        ax_p.imshow(patch_data, cmap="gray", vmin=-1, vmax=1)
        ax_p.axis("off")
        border = patches.Rectangle((0, 0), 1, 1, transform=ax_p.transAxes,
                                   linewidth=1.5, edgecolor=level["color"],
                                   facecolor="none")
        ax_p.add_patch(border)

    # Arrow to next level
    if l_idx < len(levels) - 1:
        fig.text(
            (gs[l_idx + 1].get_position(fig).x1 + gs[l_idx + 2].get_position(fig).x0) / 2,
            0.45,
            "→", ha="center", va="center",
            fontsize=24, color=FG, fontweight="bold"
        )

plt.suptitle("Ієрархія ознак у глибоких CNN — від країв до об'єктів",
             color=FG, fontsize=16, fontweight="bold", y=1.02)
plt.savefig("../img/08_feature_hierarchy.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("Saved 08_feature_hierarchy.png")
