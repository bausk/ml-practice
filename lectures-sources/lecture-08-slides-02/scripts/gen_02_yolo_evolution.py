"""Slide: YOLO evolution timeline."""
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

fig, ax = plt.subplots(figsize=(14, 5), facecolor=BG)
ax.set_facecolor(BG)
ax.set_xlim(2015.5, 2025.5)
ax.set_ylim(-1, 6)
ax.axis("off")

versions = [
    (2016, "v1", "Сітка\nОдноетапний", ACCENT),
    (2017, "v2", "Anchor boxes\nBatch Norm", ACCENT),
    (2018, "v3", "Multi-scale\nFPN", ACCENT2),
    (2020, "v4", "BoF\nCSPNet", ACCENT2),
    (2020.4, "v5", "PyTorch\nUltralytics", GOLD),
    (2023, "v8", "Anchor-free\nНова голова", WARN),
    (2024, "v11", "C3k2\nEdge-ready", PURPLE),
]

# Timeline line
ax.plot([2015.8, 2025.2], [2.5, 2.5], "-", color="#4a6fa5", linewidth=2, alpha=0.5)

for year, name, desc, color in versions:
    # Vertical line
    ax.plot([year, year], [2.5, 3.8], "-", color=color, linewidth=2, alpha=0.7)
    # Circle
    ax.plot(year, 2.5, "o", color=color, markersize=12, zorder=5)
    # Version label
    ax.text(year, 4.1, f"YOLO{name}", ha="center", va="bottom", color=color,
            fontsize=11, fontweight="bold")
    # Description
    ax.text(year, 1.5, desc, ha="center", va="top", color=FG, fontsize=8, alpha=0.8)
    # Year
    ax.text(year, 0.3, str(int(year)), ha="center", color=FG, fontsize=9, alpha=0.6)

# Speed arrow
ax.annotate("", xy=(2025, 5.5), xytext=(2016, 5.5),
            arrowprops=dict(arrowstyle="->", color=ACCENT2, lw=2))
ax.text(2020.5, 5.7, "Точність + Швидкість →", ha="center", color=ACCENT2,
        fontsize=11, fontweight="bold")

plt.suptitle("Еволюція YOLO: від ідеї до індустріального стандарту",
             color=FG, fontsize=15, fontweight="bold", y=0.98)
plt.tight_layout()
plt.savefig("../img/02_yolo_evolution.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("Saved 02_yolo_evolution.png")
