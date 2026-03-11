"""Slide: ReLU non-linearity — function plot + before/after matrix."""
import numpy as np
import matplotlib.pyplot as plt

BG = "#1a1a2e"
FG = "white"
ACCENT = "#2ecc71"

# Feature map before ReLU (some negative values)
before = np.array([
    [ 3.2, -1.4,  0.8, -2.1],
    [-0.5,  4.1, -3.0,  1.7],
    [ 2.3, -0.9,  1.1, -1.8],
    [-1.2,  0.6, -2.4,  3.5],
])
after = np.maximum(before, 0)

fig = plt.figure(figsize=(15, 5), facecolor=BG)
gs = fig.add_gridspec(1, 3, width_ratios=[1.5, 1, 1], wspace=0.4)

# Panel 0: ReLU function plot
ax0 = fig.add_subplot(gs[0])
ax0.set_facecolor(BG)
z = np.linspace(-3.5, 3.5, 300)
relu = np.maximum(z, 0)
ax0.plot(z, relu, color=ACCENT, linewidth=3, label="ReLU(z) = max(0, z)")
ax0.axhline(0, color=FG, linewidth=0.5, alpha=0.5)
ax0.axvline(0, color=FG, linewidth=0.5, alpha=0.5)
ax0.fill_between(z[z < 0], relu[z < 0], alpha=0.15, color="#e74c3c", label="обнулено")
ax0.fill_between(z[z >= 0], relu[z >= 0], alpha=0.15, color=ACCENT, label="збережено")
ax0.set_xlabel("z", color=FG)
ax0.set_ylabel("ReLU(z)", color=FG)
ax0.set_title("g(z) = max(0, z)", color=FG, fontsize=15, pad=8)
ax0.tick_params(colors=FG)
ax0.spines[["bottom", "left"]].set_color(FG)
ax0.spines[["top", "right"]].set_visible(False)
ax0.legend(fontsize=10, labelcolor=FG, facecolor="#2c3e50", edgecolor=FG)

def draw_heatmap(ax, mat, title):
    im = ax.imshow(mat, cmap="RdYlGn", vmin=-4, vmax=4)
    ax.set_title(title, color=FG, fontsize=13, pad=6)
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            v = mat[i, j]
            col = "black" if -1.5 < v < 2.5 else FG
            ax.text(j, i, f"{v:.1f}", ha="center", va="center",
                    fontsize=12, color=col, fontweight="bold")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_facecolor(BG)

ax1 = fig.add_subplot(gs[1])
draw_heatmap(ax1, before, "До ReLU")

ax2 = fig.add_subplot(gs[2])
draw_heatmap(ax2, after, "Після ReLU ✓")

# Arrow between
fig.text(0.635, 0.5, "→", ha="center", va="center",
         fontsize=28, color=ACCENT, fontweight="bold")

plt.suptitle("ReLU: від'ємні значення → 0   |   Вводить нелінійність",
             color=FG, fontsize=15, fontweight="bold", y=1.03)
plt.savefig("../img/05_relu.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("Saved 05_relu.png")
