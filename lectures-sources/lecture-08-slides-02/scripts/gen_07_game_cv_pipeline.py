"""Slide: Full scene understanding pipeline for games."""
import matplotlib.pyplot as plt
import matplotlib.patches as patches

BG = "#1a1a2e"
FG = "white"
ACCENT = "#3498db"
ACCENT2 = "#2ecc71"
WARN = "#e74c3c"
GOLD = "#f39c12"
PURPLE = "#9b59b6"

fig, ax = plt.subplots(figsize=(14, 7), facecolor=BG)
ax.set_facecolor(BG)
ax.set_xlim(-0.5, 14.5)
ax.set_ylim(-0.5, 9)
ax.set_aspect("equal")
ax.axis("off")

# Input: Game frame
input_box = patches.FancyBboxPatch((5, 7.5), 4, 1,
    boxstyle="round,pad=0.15", facecolor=GOLD, alpha=0.4, edgecolor=FG, linewidth=2)
ax.add_patch(input_box)
ax.text(7, 8.0, "Ігровий кадр (RGB)", ha="center", va="center",
        color=FG, fontsize=12, fontweight="bold")

# Three parallel processors
processors = [
    (1.5, 5.5, "YOLO\nДетекція", WARN, "Об'єкти +\nрамки + класи"),
    (6, 5.5, "DeepLab\nСегментація", ACCENT, "Семантична\nкарта сцени"),
    (10.5, 5.5, "Depth\nAnything", ACCENT2, "Карта\nглибини"),
]

# Arrows from input
for px, py, _, _, _ in processors:
    ax.annotate("", xy=(px + 1, py + 1.3), xytext=(7, 7.5),
                arrowprops=dict(arrowstyle="->", color=GOLD, lw=1.5))

for px, py, label, color, output in processors:
    box = patches.FancyBboxPatch((px, py), 2.5, 1.3,
        boxstyle="round,pad=0.15", facecolor=color, alpha=0.4, edgecolor=FG, linewidth=1.5)
    ax.add_patch(box)
    ax.text(px + 1.25, py + 0.65, label, ha="center", va="center",
            color=FG, fontsize=10, fontweight="bold")
    # Output label below
    ax.text(px + 1.25, py - 0.5, output, ha="center", va="center",
            color=color, fontsize=8, alpha=0.8)

# Fusion block
fusion_box = patches.FancyBboxPatch((3.5, 2.5), 7, 1.3,
    boxstyle="round,pad=0.2", facecolor=PURPLE, alpha=0.3, edgecolor=FG, linewidth=2)
ax.add_patch(fusion_box)
ax.text(7, 3.15, "Fusion / Інтеграція", ha="center", va="center",
        color=FG, fontsize=12, fontweight="bold")

# Arrows to fusion
for px, py, _, _, _ in processors:
    ax.annotate("", xy=(7, 3.8), xytext=(px + 1.25, py),
                arrowprops=dict(arrowstyle="->", color=PURPLE, lw=1.5, alpha=0.7))

# Fusion outputs
fusion_items = [
    (1.5, 1.5, "3D-позиції\nоб'єктів", WARN),
    (5, 1.5, "Прохідні\nзони", ACCENT),
    (8.5, 1.5, "Контекст\nсцени (CLIP)", ACCENT2),
    (12, 1.5, "Карта\nзагроз", GOLD),
]

for fx, fy, flabel, fcolor in fusion_items:
    fbox = patches.FancyBboxPatch((fx, fy), 2.3, 0.9,
        boxstyle="round,pad=0.1", facecolor=fcolor, alpha=0.2, edgecolor=fcolor, linewidth=1)
    ax.add_patch(fbox)
    ax.text(fx + 1.15, fy + 0.45, flabel, ha="center", va="center",
            color=FG, fontsize=8)

# Final arrow
ax.annotate("", xy=(7, 0.5), xytext=(7, 1.5),
            arrowprops=dict(arrowstyle="->", color=GOLD, lw=2))

# Output: Game logic
output_box = patches.FancyBboxPatch((4.5, -0.3), 5, 0.8,
    boxstyle="round,pad=0.15", facecolor=ACCENT2, alpha=0.4, edgecolor=FG, linewidth=2)
ax.add_patch(output_box)
ax.text(7, 0.1, "Ігрова логіка / RL-агент", ha="center", va="center",
        color=FG, fontsize=11, fontweight="bold")

plt.suptitle("Повний пайплайн розуміння сцени для ігрового AI",
             color=FG, fontsize=15, fontweight="bold", y=0.98)
plt.tight_layout()
plt.savefig("../img/07_game_cv_pipeline.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("Saved 07_game_cv_pipeline.png")
