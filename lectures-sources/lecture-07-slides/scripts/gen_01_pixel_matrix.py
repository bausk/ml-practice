"""Slide: Images are Numbers — shows pixel matrix of a simple grayscale image."""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

BG = "#1a1a2e"
FG = "white"

# Simple 8×8 face-like pattern (0=black, 255=white)
img = np.array([
    [220, 220, 220, 220, 220, 220, 220, 220],
    [220,  30,  30, 220, 220,  30,  30, 220],
    [220,  30,  30, 220, 220,  30,  30, 220],
    [220, 220, 220, 220, 220, 220, 220, 220],
    [220, 220, 220, 220, 220, 220, 220, 220],
    [ 30, 220, 220, 220, 220, 220, 220,  30],
    [220,  30,  30,  30,  30,  30,  30, 220],
    [220, 220, 220, 220, 220, 220, 220, 220],
], dtype=np.uint8)

fig, axes = plt.subplots(1, 3, figsize=(14, 4.5), facecolor=BG,
                         gridspec_kw={"width_ratios": [1, 0.12, 1.4]})

# Left: image
ax1 = axes[0]
ax1.imshow(img, cmap="gray", vmin=0, vmax=255)
ax1.set_title("Зображення", color=FG, fontsize=15, pad=8)
ax1.axis("off")
ax1.set_facecolor(BG)

# Middle: "=" label
axes[1].text(0.5, 0.5, "=", ha="center", va="center", fontsize=36, color=FG,
             transform=axes[1].transAxes)
axes[1].axis("off")
axes[1].set_facecolor(BG)

# Right: numeric matrix
ax2 = axes[2]
ax2.imshow(img, cmap="gray", vmin=0, vmax=255, alpha=0.25)
ax2.set_title("Матриця чисел (0 – 255)", color=FG, fontsize=15, pad=8)
for i in range(8):
    for j in range(8):
        v = img[i, j]
        c = "white" if v < 130 else "#111"
        ax2.text(j, i, str(v), ha="center", va="center",
                 fontsize=10, color=c, fontweight="bold")
ax2.set_xticks([])
ax2.set_yticks([])
ax2.set_facecolor(BG)
for sp in ax2.spines.values():
    sp.set_edgecolor("#4a4a7a")

plt.suptitle("Зображення = матриця чисел від 0 до 255",
             color=FG, fontsize=17, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig("../img/01_pixel_matrix.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("Saved 01_pixel_matrix.png")
