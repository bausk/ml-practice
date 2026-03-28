#!/usr/bin/env python3
"""
Generate images for Lecture 8: 3D Scene Understanding, SfM, and CV in Games.
All images use a warm light theme consistent with the presentation.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
import numpy as np
from pathlib import Path

OUT = Path(__file__).parent / "public" / "images"
OUT.mkdir(parents=True, exist_ok=True)

# === THEME ===
BG = "#FAF7F2"
TEXT = "#1B2332"
TEXT2 = "#5A6478"
BLUE = "#2563EB"
ORANGE = "#F97316"
EMERALD = "#10B981"
ROSE = "#E11D48"
VIOLET = "#7C3AED"
BORDER = "#E5E1DA"

plt.rcParams.update({
    "figure.facecolor": BG,
    "axes.facecolor": BG,
    "text.color": TEXT,
    "axes.labelcolor": TEXT,
    "xtick.color": TEXT2,
    "ytick.color": TEXT2,
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 13,
})


def save(fig, name):
    fig.savefig(OUT / name, dpi=200, bbox_inches="tight", pad_inches=0.3)
    plt.close(fig)
    print(f"  ✓ {name}")


# ─────────────────────────────────────────
# 1. Parallax / Triangulation diagram
# ─────────────────────────────────────────
def make_parallax():
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.set_xlim(-1, 11)
    ax.set_ylim(-0.5, 7)
    ax.set_aspect("equal")
    ax.axis("off")

    # 3D point
    ax.plot(5, 6, "o", color=EMERALD, ms=16, zorder=5)
    ax.annotate("3D точка P", (5, 6), (5.6, 6.3),
                fontsize=14, fontweight="bold", color=EMERALD)

    # Camera 1
    cam1_x, cam1_y = 1.5, 0.5
    rect1 = FancyBboxPatch((cam1_x - 0.7, cam1_y - 0.4), 1.4, 0.8,
                            boxstyle="round,pad=0.1", fc="white", ec=BLUE, lw=2.5)
    ax.add_patch(rect1)
    ax.annotate("Камера 1", (cam1_x, cam1_y - 0.7), ha="center",
                fontsize=11, fontweight="bold", color=BLUE)
    # lens
    ax.plot([cam1_x + 0.7, cam1_x + 1.1], [cam1_y, cam1_y], color=BLUE, lw=3)

    # Camera 2
    cam2_x, cam2_y = 8.5, 0.5
    rect2 = FancyBboxPatch((cam2_x - 0.7, cam2_y - 0.4), 1.4, 0.8,
                            boxstyle="round,pad=0.1", fc="white", ec=ORANGE, lw=2.5)
    ax.add_patch(rect2)
    ax.annotate("Камера 2", (cam2_x, cam2_y - 0.7), ha="center",
                fontsize=11, fontweight="bold", color=ORANGE)
    ax.plot([cam2_x - 0.7, cam2_x - 1.1], [cam2_y, cam2_y], color=ORANGE, lw=3)

    # Sight lines (dashed)
    ax.plot([cam1_x, 5], [cam1_y, 6], "--", color=BLUE, lw=1.5, alpha=0.5)
    ax.plot([cam2_x, 5], [cam2_y, 6], "--", color=ORANGE, lw=1.5, alpha=0.5)

    # Baseline
    ax.annotate("", xy=(cam2_x, 0.0), xytext=(cam1_x, 0.0),
                arrowprops=dict(arrowstyle="<->", color=TEXT2, lw=1.5))
    ax.text(5, -0.25, "Базова лінія (baseline)", ha="center", fontsize=10, color=TEXT2)

    # Image planes
    for cx, cy, col, label in [(cam1_x, cam1_y, BLUE, "x₁"), (cam2_x, cam2_y, ORANGE, "x₂")]:
        ix = cx + (5 - cx) * 0.3
        iy = cy + (6 - cy) * 0.3
        ax.plot(ix, iy, "s", color=col, ms=8, zorder=4)
        ax.annotate(label, (ix, iy), (ix + 0.3, iy - 0.3),
                    fontsize=12, fontweight="bold", color=col)

    # Title
    ax.text(5, 7.2, "Тріангуляція: два ракурси → 3D координати",
            ha="center", fontsize=16, fontweight="bold", color=TEXT)

    save(fig, "01_parallax.png")


# ─────────────────────────────────────────
# 2. SfM Pipeline (7 steps)
# ─────────────────────────────────────────
def make_sfm_pipeline():
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.set_xlim(-0.5, 14.5)
    ax.set_ylim(-1, 4.5)
    ax.axis("off")

    steps = [
        ("1", "Виділення\nознак", BLUE),
        ("2", "Зіставлення", BLUE),
        ("3", "Верифікація", BLUE),
        ("4", "Ініціалізація", ORANGE),
        ("5", "Реєстрація\nкамер", ORANGE),
        ("6", "Тріангуляція", EMERALD),
        ("7", "Bundle\nAdjustment", EMERALD),
    ]

    for i, (num, label, color) in enumerate(steps):
        x = i * 2 + 0.5
        box = FancyBboxPatch((x - 0.7, 0.8), 1.4, 2.0,
                              boxstyle="round,pad=0.15",
                              fc="white", ec=color, lw=2.5)
        ax.add_patch(box)

        # Number circle
        circ = Circle((x, 2.4), 0.3, fc=color, ec="none", zorder=5)
        ax.add_patch(circ)
        ax.text(x, 2.4, num, ha="center", va="center",
                fontsize=12, fontweight="bold", color="white", zorder=6)

        # Label
        ax.text(x, 1.5, label, ha="center", va="center",
                fontsize=9, color=TEXT, fontweight="500", linespacing=1.3)

        # Arrow
        if i < len(steps) - 1:
            ax.annotate("", xy=(x + 1.1, 1.8), xytext=(x + 0.8, 1.8),
                        arrowprops=dict(arrowstyle="->", color=TEXT2, lw=1.5))

    # Loop arrow from 7 back to 5
    ax.annotate("", xy=(8.5, 0.6), xytext=(12.5, 0.6),
                arrowprops=dict(arrowstyle="->", color=ROSE, lw=2,
                                connectionstyle="arc3,rad=0.4"))
    ax.text(10.5, -0.2, "Повтор для кожного\nнового зображення",
            ha="center", fontsize=9, color=ROSE, fontstyle="italic")

    # Phase labels
    ax.text(3, 3.8, "Від пікселів до геометрії", ha="center",
            fontsize=11, color=BLUE, fontweight="bold")
    ax.text(8.5, 3.8, "Нарощування моделі", ha="center",
            fontsize=11, color=ORANGE, fontweight="bold")
    ax.text(12.5, 3.8, "Оптимізація", ha="center",
            fontsize=11, color=EMERALD, fontweight="bold")

    ax.text(7, 4.4, "Інкрементальний SfM: 7 кроків",
            ha="center", fontsize=16, fontweight="bold", color=TEXT)

    save(fig, "02_sfm_pipeline.png")


# ─────────────────────────────────────────
# 3. Comparison chart: SfM vs related methods
# ─────────────────────────────────────────
def make_comparison():
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.axis("off")

    headers = ["", "SfM", "MVS", "SLAM", "NeRF", "3DGS"]
    colors = ["white", BLUE, ORANGE, EMERALD, VIOLET, ROSE]
    rows = [
        ["Вхід", "Фото", "SfM-результат", "Відео (live)", "Фото + SfM", "Фото + SfM"],
        ["Вихід", "Хмара + пози", "Щільний меш", "Поза + карта", "Нові ракурси", "Нові ракурси"],
        ["Швидкість", "Офлайн", "Офлайн", "30+ Hz", "Години", "30–60 хв"],
        ["Рендер", "—", "Низька", "—", "Фотореаліст.", "90+ FPS"],
    ]

    ncols = len(headers)
    nrows = len(rows)
    cell_w = 1.8
    cell_h = 0.7
    x0 = 0.5
    y0 = 4.0

    # Header row
    for j, (h, c) in enumerate(zip(headers, colors)):
        x = x0 + j * cell_w
        if j > 0:
            box = FancyBboxPatch((x, y0), cell_w - 0.1, cell_h,
                                  boxstyle="round,pad=0.05", fc=c, ec="none")
            ax.add_patch(box)
            ax.text(x + cell_w / 2 - 0.05, y0 + cell_h / 2, h,
                    ha="center", va="center", fontsize=12,
                    fontweight="bold", color="white")
        else:
            ax.text(x + cell_w / 2 - 0.05, y0 + cell_h / 2, h,
                    ha="center", va="center", fontsize=12,
                    fontweight="bold", color=TEXT)

    # Data rows
    for i, row in enumerate(rows):
        y = y0 - (i + 1) * cell_h - 0.1 * (i + 1)
        for j, cell in enumerate(row):
            x = x0 + j * cell_w
            bg = "white" if i % 2 == 0 else "#F5F2ED"
            if j == 0:
                ax.text(x + cell_w / 2 - 0.05, y + cell_h / 2, cell,
                        ha="center", va="center", fontsize=11,
                        fontweight="bold", color=TEXT)
            else:
                box = FancyBboxPatch((x, y), cell_w - 0.1, cell_h,
                                      boxstyle="round,pad=0.05", fc=bg,
                                      ec=BORDER, lw=1)
                ax.add_patch(box)
                ax.text(x + cell_w / 2 - 0.05, y + cell_h / 2, cell,
                        ha="center", va="center", fontsize=10, color=TEXT2)

    ax.set_xlim(-0.2, x0 + ncols * cell_w + 0.5)
    ax.set_ylim(y0 - (nrows + 1) * (cell_h + 0.1), y0 + cell_h + 1.0)

    ax.text(x0 + ncols * cell_w / 2, y0 + cell_h + 0.6,
            "SfM — фундамент: NeRF і 3DGS потребують COLMAP-позицій",
            ha="center", fontsize=13, fontweight="bold", color=TEXT,
            style="italic")

    save(fig, "03_comparison.png")


# ─────────────────────────────────────────
# 4. Photogrammetry-to-game pipeline
# ─────────────────────────────────────────
def make_photogrammetry_pipeline():
    fig, ax = plt.subplots(figsize=(14, 4))
    ax.set_xlim(-0.5, 15)
    ax.set_ylim(-0.5, 3.5)
    ax.axis("off")

    steps = [
        ("1", "Зйомка", "DSLR / дрон\n/ телефон", BLUE),
        ("2", "SfM", "Хмара точок\n+ пози камер", BLUE),
        ("3", "MVS", "Щільний\nмеш", ORANGE),
        ("4", "Cleanup", "Ретопологія\nUV, PBR", EMERALD),
        ("5", "Рушій", "UE5 / Unity", VIOLET),
    ]

    for i, (num, title, desc, color) in enumerate(steps):
        x = i * 3 + 0.8
        # Box
        box = FancyBboxPatch((x - 1, 0.3), 2, 2.2,
                              boxstyle="round,pad=0.15",
                              fc="white", ec=color, lw=2.5)
        ax.add_patch(box)
        # Number circle
        circ = Circle((x, 2.15), 0.3, fc=color, ec="none", zorder=5)
        ax.add_patch(circ)
        ax.text(x, 2.15, num, ha="center", va="center",
                fontsize=13, fontweight="bold", color="white", zorder=6)
        # Title
        ax.text(x, 1.5, title, ha="center", va="center",
                fontsize=13, fontweight="bold", color=color)
        # Description
        ax.text(x, 0.8, desc, ha="center", va="center",
                fontsize=9, color=TEXT2, linespacing=1.3)
        # Arrow
        if i < len(steps) - 1:
            ax.annotate("", xy=(x + 1.3, 1.4), xytext=(x + 1.0, 1.4),
                        arrowprops=dict(arrowstyle="-|>", color=TEXT2, lw=2))

    ax.text(7.5, 3.3, "Від реального світу до ігрового рівня",
            ha="center", fontsize=16, fontweight="bold", color=TEXT)

    save(fig, "04_photogrammetry_pipeline.png")


# ─────────────────────────────────────────
# 5. Point cloud visualization (abstract)
# ─────────────────────────────────────────
def make_point_cloud():
    rng = np.random.RandomState(42)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(-2, 12)
    ax.set_ylim(-1, 8)
    ax.axis("off")

    # Generate a "building-like" point cloud
    # Walls
    wx = np.concatenate([np.full(40, 0), np.full(40, 10),
                         np.linspace(0, 10, 50), np.linspace(0, 10, 50)])
    wy = np.concatenate([np.linspace(0, 6, 40), np.linspace(0, 6, 40),
                         np.full(50, 0), np.full(50, 6)])
    # Add noise
    wx += rng.normal(0, 0.15, len(wx))
    wy += rng.normal(0, 0.15, len(wy))

    # Interior points (sparse)
    ix = rng.uniform(1, 9, 60)
    iy = rng.uniform(1, 5, 60)

    all_x = np.concatenate([wx, ix])
    all_y = np.concatenate([wy, iy])

    # Color by position
    colors_arr = []
    for x, y in zip(all_x, all_y):
        t = (x + y) / 16
        r = int(37 + (124 - 37) * t)
        g = int(99 + (58 - 99) * t)
        b = int(235 + (237 - 235) * t)
        colors_arr.append(f"#{r:02x}{g:02x}{b:02x}")

    ax.scatter(all_x, all_y, c=colors_arr, s=12, alpha=0.7, edgecolors="none")

    # Camera positions
    cams = [(1, -0.5), (3.5, -0.5), (6, -0.5), (8.5, -0.5), (11, 2), (11, 4.5)]
    for cx, cy in cams:
        ax.plot(cx, cy, "^", color=ORANGE, ms=10, zorder=5)

    # FOV lines from first camera
    ax.plot([1, 0, 1], [-0.5, 0, 0], "-", color=ORANGE, lw=0.8, alpha=0.3)
    ax.plot([1, 3, 1], [-0.5, 0, 0], "-", color=ORANGE, lw=0.8, alpha=0.3)

    ax.text(5, 7.5, "Розріджена хмара точок + пози камер",
            ha="center", fontsize=16, fontweight="bold", color=TEXT)
    ax.text(5, 7.0, "Результат роботи SfM",
            ha="center", fontsize=12, color=TEXT2)

    # Legend
    ax.plot([], [], "o", color=BLUE, ms=6, label="3D точки")
    ax.plot([], [], "^", color=ORANGE, ms=8, label="Камери")
    ax.legend(loc="lower right", frameon=True, facecolor="white",
              edgecolor=BORDER, fontsize=10)

    save(fig, "05_point_cloud.png")


# ─────────────────────────────────────────
# 6. Detection vs Segmentation visual
# ─────────────────────────────────────────
def make_detection_vs_segmentation():
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))

    titles = ["Класифікація", "Детекція", "Сегментація"]
    colors_list = [BLUE, ORANGE, EMERALD]

    for ax, title, color in zip(axes, titles, colors_list):
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.set_aspect("equal")
        ax.axis("off")

        # Background "image"
        bg = np.random.RandomState(7).rand(20, 20) * 0.1 + 0.92
        ax.imshow(bg, extent=[0, 10, 0, 10], cmap="Greys", alpha=0.3, zorder=0)

        # "Object" shapes
        if title == "Класифікація":
            # Just a label
            circle = plt.Circle((5, 5), 2.5, fc=color, alpha=0.15, ec=color, lw=2)
            ax.add_patch(circle)
            ax.text(5, 5.3, "A", fontsize=36, ha="center", va="center",
                    fontweight="bold", color=color, alpha=0.4)
            ax.text(5, 4.2, "object", fontsize=11, ha="center", va="center",
                    color=TEXT2, fontstyle="italic")
            ax.text(5, 1.5, 'Mitka: "kit"', ha="center", fontsize=12,
                    fontweight="bold", color=color)

        elif title == "Детекція":
            # Bounding boxes
            rect1 = plt.Rectangle((1.5, 2.5), 4, 5, fill=False,
                                   ec=ORANGE, lw=3, linestyle="-")
            ax.add_patch(rect1)
            ax.text(1.5, 7.8, "kit 0.97", fontsize=10, fontweight="bold",
                    color="white",
                    bbox=dict(boxstyle="round,pad=0.2", fc=ORANGE, ec="none"))
            ax.text(3.5, 5, "A", fontsize=28, ha="center", va="center",
                    fontweight="bold", color=ORANGE, alpha=0.3)

            rect2 = plt.Rectangle((5.5, 1.5), 3.5, 4, fill=False,
                                   ec=VIOLET, lw=3, linestyle="-")
            ax.add_patch(rect2)
            ax.text(5.5, 5.8, "sobaka 0.91", fontsize=10, fontweight="bold",
                    color="white",
                    bbox=dict(boxstyle="round,pad=0.2", fc=VIOLET, ec="none"))
            ax.text(7.2, 3.5, "B", fontsize=24, ha="center", va="center",
                    fontweight="bold", color=VIOLET, alpha=0.3)

        elif title == "Сегментація":
            # Pixel masks
            mask = np.zeros((20, 20, 4))
            for ii in range(20):
                for jj in range(20):
                    cx, cy = jj / 2, (19 - ii) / 2
                    if (cx - 3.5)**2 + (cy - 5)**2 < 6:
                        mask[ii, jj] = [0.145, 0.388, 0.921, 0.35]
                    elif (cx - 7.2)**2 + (cy - 3.5)**2 < 4:
                        mask[ii, jj] = [0.063, 0.725, 0.506, 0.35]
            ax.imshow(mask, extent=[0, 10, 0, 10], zorder=1)
            ax.text(3.5, 5, "A", fontsize=28, ha="center", va="center",
                    fontweight="bold", color=BLUE, alpha=0.5, zorder=2)
            ax.text(7.2, 3.5, "B", fontsize=24, ha="center", va="center",
                    fontweight="bold", color=EMERALD, alpha=0.5, zorder=2)
            ax.text(5, 1.0, "Popikselna maska", ha="center", fontsize=10,
                    fontweight="bold", color=EMERALD)

        # Border
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_color(BORDER)
            spine.set_linewidth(1.5)

        ax.set_title(title, fontsize=14, fontweight="bold", color=color, pad=10)

    fig.suptitle("Задачі комп'ютерного зору: зростаюча деталізація",
                 fontsize=16, fontweight="bold", color=TEXT, y=1.02)
    fig.tight_layout()
    save(fig, "06_detection_vs_segmentation.png")


# ─────────────────────────────────────────
# 7. U-Net architecture diagram
# ─────────────────────────────────────────
def make_unet():
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_xlim(-1, 13)
    ax.set_ylim(-1, 7)
    ax.axis("off")

    # Encoder blocks (going down)
    enc_specs = [
        (0.5, 4.5, 1.5, 1.8, "Input\n256×256"),
        (2.5, 3.5, 1.5, 1.5, "Conv + Pool\n128×128"),
        (4.5, 2.5, 1.5, 1.2, "Conv + Pool\n64×64"),
        (6.5, 2.0, 1.5, 1.0, "Bottleneck\n32×32"),
    ]

    # Decoder blocks (going up)
    dec_specs = [
        (8.5, 2.5, 1.5, 1.2, "Up + Conv\n64×64"),
        (10.5, 3.5, 1.5, 1.5, "Up + Conv\n128×128"),
        (12.0, 4.5, 1.5, 1.8, "Output\n256×256"),
    ]

    # Draw encoder
    for x, y, w, h, label in enc_specs:
        color = BLUE
        box = FancyBboxPatch((x, y), w, h,
                              boxstyle="round,pad=0.1", fc="white", ec=color, lw=2)
        ax.add_patch(box)
        ax.text(x + w/2, y + h/2, label, ha="center", va="center",
                fontsize=8, color=TEXT, fontweight="500", linespacing=1.2)

    # Draw decoder
    for x, y, w, h, label in dec_specs:
        color = EMERALD
        box = FancyBboxPatch((x, y), w, h,
                              boxstyle="round,pad=0.1", fc="white", ec=color, lw=2)
        ax.add_patch(box)
        ax.text(x + w/2, y + h/2, label, ha="center", va="center",
                fontsize=8, color=TEXT, fontweight="500", linespacing=1.2)

    # Down arrows (encoder)
    for i in range(3):
        x1 = enc_specs[i][0] + enc_specs[i][2]
        y1 = enc_specs[i][1] + enc_specs[i][3] / 2
        x2 = enc_specs[i+1][0]
        y2 = enc_specs[i+1][1] + enc_specs[i+1][3] / 2
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=2))

    # Up arrows (bottleneck to decoder, decoder to decoder)
    ax.annotate("", xy=(dec_specs[0][0], dec_specs[0][1] + dec_specs[0][3]/2),
                xytext=(enc_specs[3][0] + enc_specs[3][2], enc_specs[3][1] + enc_specs[3][3]/2),
                arrowprops=dict(arrowstyle="-|>", color=EMERALD, lw=2))
    for i in range(2):
        x1 = dec_specs[i][0] + dec_specs[i][2]
        y1 = dec_specs[i][1] + dec_specs[i][3] / 2
        x2 = dec_specs[i+1][0]
        y2 = dec_specs[i+1][1] + dec_specs[i+1][3] / 2
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color=EMERALD, lw=2))

    # Skip connections
    skip_pairs = [
        (enc_specs[0], dec_specs[2]),
        (enc_specs[1], dec_specs[1]),
        (enc_specs[2], dec_specs[0]),
    ]
    for enc, dec in skip_pairs:
        x1 = enc[0] + enc[2] / 2
        y1 = enc[1] + enc[3]
        x2 = dec[0] + dec[2] / 2
        y2 = dec[1] + dec[3]
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=1.5,
                                    linestyle="--",
                                    connectionstyle="arc3,rad=-0.25"))

    # Labels
    ax.text(3.5, 6.5, "Encoder", fontsize=14, fontweight="bold", color=BLUE)
    ax.text(10, 6.5, "Decoder", fontsize=14, fontweight="bold", color=EMERALD)
    ax.text(6, 6.5, "Skip connections", fontsize=11, color=ORANGE,
            fontstyle="italic")

    ax.text(6.5, 0.2, "U-Net: encoder-decoder з skip connections",
            ha="center", fontsize=15, fontweight="bold", color=TEXT)

    save(fig, "07_unet.png")


# ─────────────────────────────────────────
# 8. Full scene understanding pipeline
# ─────────────────────────────────────────
def make_scene_pipeline():
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.set_xlim(-0.5, 15)
    ax.set_ylim(-0.5, 5)
    ax.axis("off")

    # Input
    box_in = FancyBboxPatch((0, 1.5), 1.8, 1.5,
                             boxstyle="round,pad=0.1", fc="white", ec=BLUE, lw=2.5)
    ax.add_patch(box_in)
    ax.text(0.9, 2.25, "Кадр\nз камери", ha="center", va="center",
            fontsize=10, fontweight="bold", color=BLUE, linespacing=1.3)

    # Processing branches
    branches = [
        (3.5, 3.5, "YOLO", "Детекція", ORANGE),
        (3.5, 1.8, "DeepLab", "Сегментація", EMERALD),
        (3.5, 0.1, "Depth\nAnything", "Глибина", VIOLET),
    ]
    for x, y, name, desc, color in branches:
        box = FancyBboxPatch((x, y), 2.0, 1.2,
                              boxstyle="round,pad=0.1", fc="white", ec=color, lw=2)
        ax.add_patch(box)
        ax.text(x + 1.0, y + 0.75, name, ha="center", va="center",
                fontsize=9, fontweight="bold", color=color)
        ax.text(x + 1.0, y + 0.25, desc, ha="center", va="center",
                fontsize=8, color=TEXT2)

    # Arrows from input to branches
    for _, y, _, _, _ in branches:
        ax.annotate("", xy=(3.5, y + 0.6), xytext=(1.8, 2.25),
                    arrowprops=dict(arrowstyle="-|>", color=TEXT2, lw=1.5))

    # Fusion
    box_f = FancyBboxPatch((6.5, 1.5), 1.8, 1.5,
                            boxstyle="round,pad=0.1", fc=ROSE, ec=ROSE, lw=2)
    ax.add_patch(box_f)
    ax.text(7.4, 2.25, "Fusion", ha="center", va="center",
            fontsize=12, fontweight="bold", color="white")

    # Arrows from branches to fusion
    for _, y, _, _, _ in branches:
        ax.annotate("", xy=(6.5, 2.25), xytext=(5.5, y + 0.6),
                    arrowprops=dict(arrowstyle="-|>", color=TEXT2, lw=1.5))

    # Output branches
    outputs = [
        (9.5, 3.5, "3D позиції\nоб'єктів"),
        (9.5, 1.8, "Прохідні\nзони"),
        (9.5, 0.1, "Семантичний\nконтекст"),
    ]
    for x, y, label in outputs:
        box = FancyBboxPatch((x, y), 2.0, 1.2,
                              boxstyle="round,pad=0.1", fc="#F5F2ED", ec=BORDER, lw=1.5)
        ax.add_patch(box)
        ax.text(x + 1.0, y + 0.6, label, ha="center", va="center",
                fontsize=9, color=TEXT, linespacing=1.3)

    for _, y, _ in outputs:
        ax.annotate("", xy=(9.5, y + 0.6), xytext=(8.3, 2.25),
                    arrowprops=dict(arrowstyle="-|>", color=TEXT2, lw=1.5))

    # Game logic
    box_game = FancyBboxPatch((12.5, 1.5), 2.0, 1.5,
                               boxstyle="round,pad=0.1", fc="white", ec=BLUE, lw=2.5)
    ax.add_patch(box_game)
    ax.text(13.5, 2.25, "Ігрова\nлогіка", ha="center", va="center",
            fontsize=11, fontweight="bold", color=BLUE, linespacing=1.3)

    for _, y, _ in outputs:
        ax.annotate("", xy=(12.5, 2.25), xytext=(11.5, y + 0.6),
                    arrowprops=dict(arrowstyle="-|>", color=TEXT2, lw=1.5))

    ax.text(7.5, 4.7, "Повний пайплайн розуміння сцени",
            ha="center", fontsize=16, fontweight="bold", color=TEXT)

    save(fig, "08_scene_pipeline.png")


# ─────────────────────────────────────────
# 9. Hybrid workflow diagram (SfM → 3DGS + mesh)
# ─────────────────────────────────────────
def make_hybrid_workflow():
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.set_xlim(-0.5, 13)
    ax.set_ylim(-0.5, 5)
    ax.axis("off")

    # Source
    box_src = FancyBboxPatch((0, 1.8), 2.0, 1.4,
                              boxstyle="round,pad=0.12", fc="white", ec=BLUE, lw=2.5)
    ax.add_patch(box_src)
    ax.text(1.0, 2.5, "Відео / фото\nз телефону", ha="center", va="center",
            fontsize=10, fontweight="bold", color=BLUE, linespacing=1.3)

    # COLMAP
    box_col = FancyBboxPatch((3.2, 1.8), 2.0, 1.4,
                              boxstyle="round,pad=0.12", fc="white", ec=BLUE, lw=2.5)
    ax.add_patch(box_col)
    ax.text(4.2, 2.5, "COLMAP\n(SfM)", ha="center", va="center",
            fontsize=10, fontweight="bold", color=BLUE, linespacing=1.3)

    ax.annotate("", xy=(3.2, 2.5), xytext=(2.0, 2.5),
                arrowprops=dict(arrowstyle="-|>", color=TEXT2, lw=2))

    # Branch: 3DGS
    box_gs = FancyBboxPatch((6.5, 3.2), 2.5, 1.2,
                             boxstyle="round,pad=0.12", fc="white", ec=VIOLET, lw=2.5)
    ax.add_patch(box_gs)
    ax.text(7.75, 3.8, "3DGS / Nerfstudio\nВізуальний фон", ha="center", va="center",
            fontsize=9, fontweight="bold", color=VIOLET, linespacing=1.3)

    # Branch: MVS
    box_mvs = FancyBboxPatch((6.5, 0.8), 2.5, 1.2,
                              boxstyle="round,pad=0.12", fc="white", ec=ORANGE, lw=2.5)
    ax.add_patch(box_mvs)
    ax.text(7.75, 1.4, "MVS / OpenMVS\nМеш для колізій", ha="center", va="center",
            fontsize=9, fontweight="bold", color=ORANGE, linespacing=1.3)

    ax.annotate("", xy=(6.5, 3.8), xytext=(5.2, 2.5),
                arrowprops=dict(arrowstyle="-|>", color=TEXT2, lw=2))
    ax.annotate("", xy=(6.5, 1.4), xytext=(5.2, 2.5),
                arrowprops=dict(arrowstyle="-|>", color=TEXT2, lw=2))

    # UE5
    box_ue = FancyBboxPatch((10.2, 1.8), 2.2, 1.4,
                             boxstyle="round,pad=0.12", fc=EMERALD, ec=EMERALD, lw=2)
    ax.add_patch(box_ue)
    ax.text(11.3, 2.5, "Unreal\nEngine 5", ha="center", va="center",
            fontsize=11, fontweight="bold", color="white", linespacing=1.3)

    ax.annotate("", xy=(10.2, 2.8), xytext=(9.0, 3.8),
                arrowprops=dict(arrowstyle="-|>", color=TEXT2, lw=2))
    ax.annotate("", xy=(10.2, 2.2), xytext=(9.0, 1.4),
                arrowprops=dict(arrowstyle="-|>", color=TEXT2, lw=2))

    ax.text(6.5, 4.8, "Гібридний конвеєр: поточна найкраща практика",
            ha="center", fontsize=15, fontweight="bold", color=TEXT)

    save(fig, "09_hybrid_workflow.png")


# ─────────────────────────────────────────
# 10. RL environments pipeline
# ─────────────────────────────────────────
def make_rl_pipeline():
    fig, ax = plt.subplots(figsize=(13, 4.5))
    ax.set_xlim(-0.5, 14)
    ax.set_ylim(-0.5, 4.5)
    ax.axis("off")

    steps = [
        ("RGB-D скан\nабо SfM+MVS", BLUE),
        ("Меш +\nсемантика", ORANGE),
        ("Симулятор\n(Habitat, iGibson)", EMERALD),
        ("RL агент\nтренування", ROSE),
        ("Розгортання\nу грі", VIOLET),
    ]

    for i, (label, color) in enumerate(steps):
        x = i * 2.8 + 0.5
        box = FancyBboxPatch((x, 1.0), 2.2, 2.0,
                              boxstyle="round,pad=0.12", fc="white", ec=color, lw=2.5)
        ax.add_patch(box)
        ax.text(x + 1.1, 2.0, label, ha="center", va="center",
                fontsize=10, fontweight="bold", color=color, linespacing=1.3)

        if i < len(steps) - 1:
            ax.annotate("", xy=(x + 2.5, 2.0), xytext=(x + 2.2, 2.0),
                        arrowprops=dict(arrowstyle="-|>", color=TEXT2, lw=2))

    ax.text(7, 3.8, "Від сканування до тренованого RL-агента",
            ha="center", fontsize=15, fontweight="bold", color=TEXT)
    ax.text(7, 0.3, "Скан реальної будівлі → готове тренувальне середовище за годину",
            ha="center", fontsize=11, color=TEXT2, fontstyle="italic")

    save(fig, "10_rl_pipeline.png")


# ─────────────────────────────────────────
# RUN ALL
# ─────────────────────────────────────────
if __name__ == "__main__":
    print("Generating images for Lecture 8...")
    make_parallax()
    make_sfm_pipeline()
    make_comparison()
    make_photogrammetry_pipeline()
    make_point_cloud()
    make_detection_vs_segmentation()
    make_unet()
    make_scene_pipeline()
    make_hybrid_workflow()
    make_rl_pipeline()
    print(f"\nDone! {len(list(OUT.glob('*.png')))} images in {OUT}")
