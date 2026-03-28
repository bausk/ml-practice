"""Slide: SfM Pipeline — 7-step flowchart."""
import matplotlib.pyplot as plt
import matplotlib.patches as patches

BG = "#1a1a2e"
FG = "white"
ACCENT = "#3498db"
ACCENT2 = "#2ecc71"
GOLD = "#f39c12"

steps = [
    ("1. Виділення\nознак", "SIFT / SuperPoint"),
    ("2. Зіставлення\nознак", "дескриптори"),
    ("3. Геометрична\nверифікація", "RANSAC + F-матриця"),
    ("4. Ініціалізація", "seed-пара → тріангуляція"),
    ("5. Реєстрація\nкамер", "PnP"),
    ("6. Тріангуляція", "нові 3D-точки"),
    ("7. Bundle\nAdjustment", "мін. помилки репроекції"),
]

fig, ax = plt.subplots(figsize=(14, 4.5), facecolor=BG)
ax.set_facecolor(BG)
ax.set_xlim(-0.5, 14.5)
ax.set_ylim(-1.2, 3.2)
ax.axis("off")

box_w = 1.6
box_h = 1.2
y_center = 1.5
gap = 0.3

colors = [ACCENT, ACCENT, ACCENT, GOLD, ACCENT2, ACCENT2, "#e74c3c"]

for i, (title, detail) in enumerate(steps):
    x = i * (box_w + gap) + 0.3
    color = colors[i]
    rect = patches.FancyBboxPatch((x, y_center - box_h / 2), box_w, box_h,
                                   boxstyle="round,pad=0.12", facecolor=color,
                                   edgecolor="white", linewidth=1.2, alpha=0.85)
    ax.add_patch(rect)
    ax.text(x + box_w / 2, y_center + 0.12, title, ha="center", va="center",
            color="white", fontsize=8.5, fontweight="bold", linespacing=1.2)
    ax.text(x + box_w / 2, y_center - 0.45, detail, ha="center", va="center",
            color="white", fontsize=6.5, alpha=0.8, style="italic")

    # Arrow to next
    if i < len(steps) - 1:
        ax.annotate("", xy=(x + box_w + gap * 0.1, y_center),
                     xytext=(x + box_w + 0.02, y_center),
                     arrowprops=dict(arrowstyle="->", color="white", lw=1.5))

# Loop arrow from BA back to step 5
x_ba = 6 * (box_w + gap) + 0.3
x_reg = 4 * (box_w + gap) + 0.3
ax.annotate("", xy=(x_reg + box_w / 2, y_center - box_h / 2 - 0.15),
            xytext=(x_ba + box_w / 2, y_center - box_h / 2 - 0.15),
            arrowprops=dict(arrowstyle="->", color=GOLD, lw=1.5,
                          connectionstyle="arc3,rad=0.3"))
ax.text((x_ba + x_reg + box_w) / 2, -0.7, "повторювати для кожного нового зображення",
        ha="center", va="center", color=GOLD, fontsize=8, style="italic")

# Output label
ax.text(x_ba + box_w + 0.3, y_center + 0.6, "Результат:\nрозріджена хмара\n+ пози камер",
        ha="left", va="center", color=FG, fontsize=8.5,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#2c3e50", edgecolor="white", alpha=0.7))

plt.suptitle("Інкрементальний SfM: 7 кроків від фотографій до 3D",
             color=FG, fontsize=14, fontweight="bold", y=1.0)
plt.tight_layout()
plt.savefig("../img/02_sfm_pipeline.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("Saved 02_sfm_pipeline.png")
