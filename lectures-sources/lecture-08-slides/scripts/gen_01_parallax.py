"""Slide: Parallax intuition — two camera positions triangulate a 3D point."""
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

BG = "#1a1a2e"
FG = "white"
ACCENT = "#3498db"
ACCENT2 = "#2ecc71"
WARN = "#e74c3c"
GOLD = "#f39c12"

fig, ax = plt.subplots(figsize=(12, 5.5), facecolor=BG)
ax.set_facecolor(BG)
ax.set_xlim(-1, 11)
ax.set_ylim(-0.5, 6.5)
ax.set_aspect("equal")
ax.axis("off")

# 3D point
px, py = 5, 5.5
ax.plot(px, py, "o", color=GOLD, markersize=14, zorder=5)
ax.text(px + 0.3, py + 0.15, "3D точка (X, Y, Z)", color=GOLD, fontsize=12, fontweight="bold")

# Camera 1 (left)
c1x, c1y = 1.5, 0.5
rect1 = patches.FancyBboxPatch((c1x - 0.6, c1y - 0.35), 1.2, 0.7,
                                boxstyle="round,pad=0.1", facecolor=ACCENT, edgecolor="white", linewidth=1.5)
ax.add_patch(rect1)
ax.text(c1x, c1y, "Камера 1", ha="center", va="center", color="white", fontsize=9, fontweight="bold")

# Camera 2 (right)
c2x, c2y = 8.5, 0.5
rect2 = patches.FancyBboxPatch((c2x - 0.6, c2y - 0.35), 1.2, 0.7,
                                boxstyle="round,pad=0.1", facecolor=ACCENT2, edgecolor="white", linewidth=1.5)
ax.add_patch(rect2)
ax.text(c2x, c2y, "Камера 2", ha="center", va="center", color="white", fontsize=9, fontweight="bold")

# Rays from cameras to 3D point
ax.plot([c1x, px], [c1y + 0.35, py], "--", color=ACCENT, linewidth=1.5, alpha=0.8)
ax.plot([c2x, px], [c2y + 0.35, py], "--", color=ACCENT2, linewidth=1.5, alpha=0.8)

# Image planes
ip1_x = 2.5
ip1_y_bot, ip1_y_top = 1.5, 3.5
ax.plot([ip1_x, ip1_x], [ip1_y_bot, ip1_y_top], "-", color="white", linewidth=2, alpha=0.5)
ax.text(ip1_x - 0.15, ip1_y_top + 0.2, "Фото 1", color="white", fontsize=9, ha="center", alpha=0.7)

ip2_x = 7.5
ip2_y_bot, ip2_y_top = 1.5, 3.5
ax.plot([ip2_x, ip2_x], [ip2_y_bot, ip2_y_top], "-", color="white", linewidth=2, alpha=0.5)
ax.text(ip2_x + 0.15, ip2_y_top + 0.2, "Фото 2", color="white", fontsize=9, ha="center", alpha=0.7)

# Projected points on image planes
t1 = (ip1_x - c1x) / (px - c1x)
proj1_y = c1y + t1 * (py - c1y)
ax.plot(ip1_x, proj1_y, "o", color=WARN, markersize=8, zorder=5)
ax.text(ip1_x + 0.3, proj1_y - 0.15, "x₁", color=WARN, fontsize=11, fontweight="bold")

t2 = (ip2_x - c2x) / (px - c2x)
proj2_y = c2y + t2 * (py - c2y)
ax.plot(ip2_x, proj2_y, "o", color=WARN, markersize=8, zorder=5)
ax.text(ip2_x - 0.55, proj2_y - 0.15, "x₂", color=WARN, fontsize=11, fontweight="bold")

# Baseline arrow
ax.annotate("", xy=(c2x - 0.7, -0.1), xytext=(c1x + 0.7, -0.1),
            arrowprops=dict(arrowstyle="<->", color=GOLD, lw=1.5))
ax.text(5, -0.35, "Базова лінія (baseline)", ha="center", color=GOLD, fontsize=10)

plt.suptitle("Паралакс: дві камери → тріангуляція 3D-точки",
             color=FG, fontsize=15, fontweight="bold", y=0.98)
plt.tight_layout()
plt.savefig("../img/01_parallax.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("Saved 01_parallax.png")
