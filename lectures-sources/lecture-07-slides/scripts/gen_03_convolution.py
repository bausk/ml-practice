"""Slide: The Convolution Operation — 5×5 image × 3×3 filter → feature map."""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

BG = "#1a1a2e"
FG = "white"
HIGHLIGHT = "#f39c12"
FILTER_C = "#2980b9"
OUTPUT_C = "#27ae60"

# 5×5 input image (from the MIT slides)
image = np.array([
    [1, 1, 1, 0, 0],
    [0, 1, 1, 1, 0],
    [0, 0, 1, 1, 1],
    [0, 0, 1, 1, 0],
    [0, 1, 1, 0, 0],
], dtype=float)

# 3×3 filter
filt = np.array([
    [1, 0, 1],
    [0, 1, 0],
    [1, 0, 1],
], dtype=float)

# Compute full feature map
h, w = image.shape
fh, fw = filt.shape
out_h, out_w = h - fh + 1, w - fw + 1
feature_map = np.zeros((out_h, out_w))
for i in range(out_h):
    for j in range(out_w):
        feature_map[i, j] = np.sum(image[i:i+fh, j:j+fw] * filt)

fig, axes = plt.subplots(1, 5, figsize=(16, 4), facecolor=BG,
                         gridspec_kw={"width_ratios": [2, 0.4, 1.2, 0.4, 1.5]})

def draw_matrix(ax, mat, title, cell_color=None, highlight_rect=None,
                text_scale=1.0, bg=BG, fmt="{:.0f}"):
    rows, cols = mat.shape
    norm = plt.Normalize(vmin=mat.min() - 0.1, vmax=mat.max() + 0.1)
    cmap = plt.cm.Blues if cell_color == "blue" else (
           plt.cm.Greens if cell_color == "green" else plt.cm.gray)
    ax.imshow(mat, cmap=cmap, vmin=-0.2, vmax=mat.max() + 0.5, alpha=0.8)
    ax.set_title(title, color=FG, fontsize=12, pad=5)
    for i in range(rows):
        for j in range(cols):
            v = mat[i, j]
            col = "white" if v < 0.6 else "black"
            ax.text(j, i, fmt.format(v), ha="center", va="center",
                    fontsize=12 * text_scale, color=col, fontweight="bold")
    if highlight_rect is not None:
        r, c = highlight_rect
        rect = patches.Rectangle((c - 0.5, r - 0.5), fw, fh,
                                  linewidth=3, edgecolor=HIGHLIGHT, facecolor="none",
                                  zorder=10)
        ax.add_patch(rect)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_facecolor(bg)

# Panel 0: image with highlighted 3×3 patch at top-left
draw_matrix(axes[0], image, "Вхідне зображення (5×5)", highlight_rect=(0, 0))

# Panel 1: "⊗"
axes[1].text(0.5, 0.5, "⊗", ha="center", va="center",
             fontsize=32, color=FILTER_C, transform=axes[1].transAxes)
axes[1].axis("off")
axes[1].set_facecolor(BG)

# Panel 2: filter
draw_matrix(axes[2], filt, "Фільтр (3×3)", cell_color="blue", text_scale=1.1)

# Panel 3: "="
axes[3].text(0.5, 0.5, "=", ha="center", va="center",
             fontsize=32, color=OUTPUT_C, transform=axes[3].transAxes)
axes[3].axis("off")
axes[3].set_facecolor(BG)

# Panel 4: feature map with annotation on first cell
draw_matrix(axes[4], feature_map, "Карта ознак (3×3)", cell_color="green", fmt="{:.0f}")

# Annotation box showing the computation
props = dict(boxstyle="round", facecolor="#2c3e50", alpha=0.9)
computation = "Крок 1: поелементне\nмноження → сума\n= 4"
axes[4].text(1.05, 0.95, computation, transform=axes[4].transAxes,
             fontsize=9.5, color=FG, va="top", bbox=props)

plt.suptitle("Операція згортки: фільтр ковзає по зображенню → карта ознак",
             color=FG, fontsize=15, fontweight="bold", y=1.04)
plt.tight_layout()
plt.savefig("../img/03_convolution.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("Saved 03_convolution.png")
