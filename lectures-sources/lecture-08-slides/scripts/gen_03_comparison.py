"""Slide: Visual comparison of SfM vs SLAM vs NeRF vs 3DGS."""
import matplotlib.pyplot as plt
import numpy as np

BG = "#1a1a2e"
FG = "white"

methods = ["SfM", "MVS", "SLAM", "NeRF", "3D Gaussian\nSplatting"]
categories = ["Геом. точність", "Якість рендеру", "Швидкість", "Редагованість"]

# Scores (0-5 scale)
scores = np.array([
    [5, 1, 2, 4],   # SfM
    [4, 2, 2, 4],   # MVS
    [3, 1, 5, 2],   # SLAM
    [3, 5, 1, 1],   # NeRF
    [2, 5, 5, 2],   # 3DGS
])

colors = ["#3498db", "#1abc9c", "#e67e22", "#9b59b6", "#e74c3c"]

fig, ax = plt.subplots(figsize=(12, 5), facecolor=BG)
ax.set_facecolor(BG)

bar_height = 0.15
y_positions = np.arange(len(categories))

for i, (method, color) in enumerate(zip(methods, colors)):
    offset = (i - len(methods) / 2 + 0.5) * bar_height
    bars = ax.barh(y_positions + offset, scores[i], bar_height * 0.9,
                   label=method, color=color, alpha=0.85, edgecolor="white", linewidth=0.3)

ax.set_yticks(y_positions)
ax.set_yticklabels(categories, color=FG, fontsize=12)
ax.set_xlim(0, 5.5)
ax.set_xticks([1, 2, 3, 4, 5])
ax.set_xticklabels(["Низька", "Помірна", "Середня", "Висока", "Найвища"],
                   color=FG, fontsize=9)
ax.tick_params(colors=FG)
ax.spines["bottom"].set_color("#4a4a7a")
ax.spines["left"].set_color("#4a4a7a")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

ax.legend(loc="lower right", fontsize=9, facecolor="#2c3e50", edgecolor="white",
          labelcolor="white", framealpha=0.9)

plt.suptitle("Порівняння методів 3D-реконструкції",
             color=FG, fontsize=14, fontweight="bold", y=0.98)
plt.tight_layout()
plt.savefig("../img/03_comparison.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("Saved 03_comparison.png")
