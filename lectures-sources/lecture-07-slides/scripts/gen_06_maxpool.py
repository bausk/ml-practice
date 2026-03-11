"""Slide: Max Pooling 2×2 — visual explanation with 4×4 → 2×2."""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

BG = "#1a1a2e"
FG = "white"

mat = np.array([
    [1, 1, 2, 4],
    [5, 6, 7, 8],
    [3, 2, 1, 0],
    [1, 2, 3, 4],
], dtype=float)

result = np.array([
    [6, 8],
    [3, 4],
], dtype=float)

block_colors = ["#2980b9", "#8e44ad", "#27ae60", "#e67e22"]
block_positions = [
    [(0, 0), (0, 1), (1, 0), (1, 1)],  # top-left block
    [(0, 2), (0, 3), (1, 2), (1, 3)],  # top-right block
    [(2, 0), (2, 1), (3, 0), (3, 1)],  # bottom-left block
    [(2, 2), (2, 3), (3, 2), (3, 3)],  # bottom-right block
]
max_positions = [(1, 1), (1, 3), (2, 0), (3, 3)]  # positions of maxima

fig, axes = plt.subplots(1, 3, figsize=(13, 5),
                         gridspec_kw={"width_ratios": [2, 0.4, 1.5]},
                         facecolor=BG)

# Panel 0: 4×4 input with colored blocks
ax0 = axes[0]
ax0.set_xlim(-0.5, 3.5)
ax0.set_ylim(3.5, -0.5)
ax0.set_facecolor(BG)
ax0.set_title("Вхідна карта ознак (4×4)", color=FG, fontsize=13, pad=8)

for b_idx, (positions, color, max_pos) in enumerate(
        zip(block_positions, block_colors, max_positions)):
    # Draw block background
    r_min = min(p[0] for p in positions)
    c_min = min(p[1] for p in positions)
    rect = patches.Rectangle((c_min - 0.5, r_min - 0.5), 2, 2,
                              linewidth=0, facecolor=color, alpha=0.25)
    ax0.add_patch(rect)
    rect2 = patches.Rectangle((c_min - 0.5, r_min - 0.5), 2, 2,
                               linewidth=2.5, edgecolor=color, facecolor="none")
    ax0.add_patch(rect2)

for i in range(4):
    for j in range(4):
        is_max = any((i, j) == mp for mp in max_positions)
        col = "gold" if is_max else FG
        weight = "bold" if is_max else "normal"
        fs = 15 if is_max else 13
        ax0.text(j, i, f"{int(mat[i,j])}", ha="center", va="center",
                 fontsize=fs, color=col, fontweight=weight)

ax0.set_xticks([])
ax0.set_yticks([])
ax0.axhline(1.5, color="#555", linewidth=1.5, linestyle="--")
ax0.axvline(1.5, color="#555", linewidth=1.5, linestyle="--")

# Panel 1: arrow
axes[1].text(0.5, 0.5, "max\n→", ha="center", va="center",
             fontsize=18, color="gold", transform=axes[1].transAxes,
             fontweight="bold")
axes[1].axis("off")
axes[1].set_facecolor(BG)

# Panel 2: 2×2 output
ax1 = axes[2]
ax1.set_facecolor(BG)
ax1.set_title("Вихід MaxPool (2×2)", color=FG, fontsize=13, pad=8)
for b_idx, (color, (ri, ci)) in enumerate(zip(block_colors, [(0,0),(0,1),(1,0),(1,1)])):
    rect = patches.Rectangle((ci - 0.5, ri - 0.5), 1, 1,
                              linewidth=0, facecolor=color, alpha=0.45)
    ax1.add_patch(rect)
    rect2 = patches.Rectangle((ci - 0.5, ri - 0.5), 1, 1,
                               linewidth=2, edgecolor=color, facecolor="none")
    ax1.add_patch(rect2)
    ax1.text(ci, ri, f"{int(result[ri,ci])}", ha="center", va="center",
             fontsize=20, color="gold", fontweight="bold")

ax1.set_xlim(-0.5, 1.5)
ax1.set_ylim(1.5, -0.5)
ax1.set_xticks([])
ax1.set_yticks([])

plt.suptitle("Max Pooling 2×2:  Зменшення розміру + інваріантність до зсувів",
             color=FG, fontsize=15, fontweight="bold", y=1.03)
plt.tight_layout()
plt.savefig("../img/06_maxpool.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("Saved 06_maxpool.png")
