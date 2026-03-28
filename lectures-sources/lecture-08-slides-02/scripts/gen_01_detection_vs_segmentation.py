"""Slide: Detection vs Segmentation — visual comparison of CV tasks."""
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

BG = "#1a1a2e"
FG = "white"
ACCENT = "#3498db"
ACCENT2 = "#2ecc71"
WARN = "#e74c3c"
GOLD = "#f39c12"
PURPLE = "#9b59b6"

fig, axes = plt.subplots(1, 3, figsize=(14, 5), facecolor=BG)

for ax in axes:
    ax.set_facecolor(BG)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_aspect("equal")
    ax.axis("off")

# --- Panel 1: Classification ---
ax1 = axes[0]
ax1.set_title("Класифікація", color=ACCENT, fontsize=14, fontweight="bold", pad=10)
# Simple scene with objects
circle1 = plt.Circle((3, 6), 1.5, color=ACCENT, alpha=0.3)
ax1.add_patch(circle1)
rect1 = patches.FancyBboxPatch((5.5, 3), 3, 2.5, boxstyle="round,pad=0.2", facecolor=ACCENT2, alpha=0.3, edgecolor="none")
ax1.add_patch(rect1)
triangle = plt.Polygon([[2, 2], [4.5, 2], [3.25, 4]], color=GOLD, alpha=0.3)
ax1.add_patch(triangle)
# Label
ax1.text(5, 0.5, '"Ігрова сцена"', ha="center", color=FG, fontsize=11, fontstyle="italic")
ax1.text(5, 9.2, "Що?", ha="center", color=ACCENT, fontsize=12, fontweight="bold")

# --- Panel 2: Detection ---
ax2 = axes[1]
ax2.set_title("Детекція", color=ACCENT2, fontsize=14, fontweight="bold", pad=10)
circle2 = plt.Circle((3, 6), 1.5, color=ACCENT, alpha=0.3)
ax2.add_patch(circle2)
rect2_obj = patches.FancyBboxPatch((5.5, 3), 3, 2.5, boxstyle="round,pad=0.2", facecolor=ACCENT2, alpha=0.3, edgecolor="none")
ax2.add_patch(rect2_obj)
triangle2 = plt.Polygon([[2, 2], [4.5, 2], [3.25, 4]], color=GOLD, alpha=0.3)
ax2.add_patch(triangle2)
# Bounding boxes
bbox1 = patches.Rectangle((1.2, 4.2), 3.6, 3.6, linewidth=2, edgecolor=WARN, facecolor="none", linestyle="--")
ax2.add_patch(bbox1)
ax2.text(1.3, 8, "Ворог 0.92", color=WARN, fontsize=9, fontweight="bold")
bbox2 = patches.Rectangle((5.2, 2.7), 3.6, 3.1, linewidth=2, edgecolor=ACCENT, facecolor="none", linestyle="--")
ax2.add_patch(bbox2)
ax2.text(5.3, 6, "Укриття 0.87", color=ACCENT, fontsize=9, fontweight="bold")
bbox3 = patches.Rectangle((1.7, 1.7), 3.1, 2.6, linewidth=2, edgecolor=GOLD, facecolor="none", linestyle="--")
ax2.add_patch(bbox3)
ax2.text(1.8, 4.5, "Зброя 0.95", color=GOLD, fontsize=9, fontweight="bold")
ax2.text(5, 9.2, "Що + Де?", ha="center", color=ACCENT2, fontsize=12, fontweight="bold")

# --- Panel 3: Segmentation ---
ax3 = axes[2]
ax3.set_title("Сегментація", color=PURPLE, fontsize=14, fontweight="bold", pad=10)
# Filled regions with distinct colors
circle3 = plt.Circle((3, 6), 1.5, color=WARN, alpha=0.5)
ax3.add_patch(circle3)
rect3 = patches.FancyBboxPatch((5.5, 3), 3, 2.5, boxstyle="round,pad=0.2", facecolor=ACCENT, alpha=0.5, edgecolor="none")
ax3.add_patch(rect3)
triangle3 = plt.Polygon([[2, 2], [4.5, 2], [3.25, 4]], color=GOLD, alpha=0.5)
ax3.add_patch(triangle3)
# Background fill
bg_rect = patches.Rectangle((0, 0), 10, 10, facecolor=PURPLE, alpha=0.15, zorder=0)
ax3.add_patch(bg_rect)
# Legend
ax3.text(5, 0.8, "Кожен піксель → клас", ha="center", color=FG, fontsize=10)
ax3.text(5, 9.2, "Що + Точна маска?", ha="center", color=PURPLE, fontsize=12, fontweight="bold")

plt.suptitle("Задачі комп'ютерного зору", color=FG, fontsize=16, fontweight="bold", y=1.0)
plt.tight_layout()
plt.savefig("../img/01_detection_vs_segmentation.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("Saved 01_detection_vs_segmentation.png")
