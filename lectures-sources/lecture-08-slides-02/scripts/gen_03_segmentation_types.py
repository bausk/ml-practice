"""Slide: Three types of segmentation comparison."""
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

fig, axes = plt.subplots(1, 3, figsize=(14, 5.5), facecolor=BG)

colors_persons = [WARN, ACCENT, GOLD]
titles = ["Семантична", "Інстансна", "Паноптична"]
title_colors = [ACCENT, ACCENT2, PURPLE]

for idx, (ax, title, tc) in enumerate(zip(axes, titles, title_colors)):
    ax.set_facecolor(BG)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, color=tc, fontsize=14, fontweight="bold", pad=10)

    # Ground / sky background
    sky = patches.Rectangle((0, 5), 10, 5, facecolor="#1e3a5f", alpha=0.3)
    ground = patches.Rectangle((0, 0), 10, 5, facecolor="#2d4a2d", alpha=0.3)
    ax.add_patch(sky)
    ax.add_patch(ground)

    if idx == 0:  # Semantic - all persons same color, background labeled
        for cx in [2.5, 5, 7.5]:
            person = patches.FancyBboxPatch((cx-0.6, 3), 1.2, 3.5,
                boxstyle="round,pad=0.15", facecolor=WARN, alpha=0.6, edgecolor="none")
            ax.add_patch(person)
        ax.text(5, 1.2, '"Людина"', ha="center", color=WARN, fontsize=11, fontweight="bold")
        ax.text(2, 8, '"Небо"', ha="center", color="#5599cc", fontsize=10)
        ax.text(8, 2.5, '"Земля"', ha="center", color=ACCENT2, fontsize=10)
        ax.text(5, 9.5, "Клас ≠ екземпляр", ha="center", color=FG, fontsize=9, alpha=0.7)

    elif idx == 1:  # Instance - each person different color
        for i, cx in enumerate([2.5, 5, 7.5]):
            person = patches.FancyBboxPatch((cx-0.6, 3), 1.2, 3.5,
                boxstyle="round,pad=0.15", facecolor=colors_persons[i], alpha=0.6, edgecolor="none")
            ax.add_patch(person)
            ax.text(cx, 2.3, f"#{i+1}", ha="center", color=colors_persons[i], fontsize=10, fontweight="bold")
        ax.text(5, 1.2, "3 окремі маски", ha="center", color=FG, fontsize=10)
        ax.text(5, 9.5, "Кожен об'єкт окремо", ha="center", color=FG, fontsize=9, alpha=0.7)

    else:  # Panoptic - instances + stuff
        for i, cx in enumerate([2.5, 5, 7.5]):
            person = patches.FancyBboxPatch((cx-0.6, 3), 1.2, 3.5,
                boxstyle="round,pad=0.15", facecolor=colors_persons[i], alpha=0.6, edgecolor="none")
            ax.add_patch(person)
            ax.text(cx, 2.3, f"#{i+1}", ha="center", color=colors_persons[i], fontsize=10, fontweight="bold")
        ax.text(2, 8, '"Небо"', ha="center", color="#5599cc", fontsize=10)
        ax.text(8, 2.5, '"Земля"', ha="center", color=ACCENT2, fontsize=10)
        ax.text(5, 1.2, "Речі + Об'єкти", ha="center", color=FG, fontsize=10)
        ax.text(5, 9.5, "Повне розуміння", ha="center", color=FG, fontsize=9, alpha=0.7)

plt.suptitle("Три типи сегментації", color=FG, fontsize=16, fontweight="bold", y=1.0)
plt.tight_layout()
plt.savefig("../img/03_segmentation_types.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("Saved 03_segmentation_types.png")
