"""Slide: Feature Maps — same image, different filters, different outputs."""
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import convolve

BG = "#1a1a2e"
FG = "white"

# Synthetic image: diagonal stripe pattern + rectangle
img = np.zeros((32, 32), dtype=float)
for i in range(32):
    for j in range(32):
        if abs(i - j) < 4:
            img[i, j] = 1.0
img[8:18, 18:28] = 0.7
img[4:6, :] = 0.5
img[:, 4:6] = 0.5

# Filters
filters = {
    "Оригінал": None,
    "Виявлення\nгоризонтальних країв": np.array([[ 1,  2,  1],
                                                  [ 0,  0,  0],
                                                  [-1, -2, -1]], dtype=float),
    "Виявлення\nвертикальних країв":  np.array([[ 1,  0, -1],
                                                  [ 2,  0, -2],
                                                  [ 1,  0, -1]], dtype=float),
    "Загострення\n(sharpen)":         np.array([[ 0, -1,  0],
                                                  [-1,  5, -1],
                                                  [ 0, -1,  0]], dtype=float),
}

fig, axes = plt.subplots(1, 4, figsize=(16, 4.5), facecolor=BG)

for ax, (name, flt) in zip(axes, filters.items()):
    if flt is None:
        result = img
        cmap = "gray"
    else:
        result = convolve(img, flt)
        result = np.clip(result, 0, None)
        cmap = "hot"

    ax.imshow(result, cmap=cmap, vmin=0)
    ax.set_title(name, color=FG, fontsize=12, pad=6)
    ax.axis("off")
    ax.set_facecolor(BG)

plt.suptitle("Різні фільтри → різні карти ознак (feature maps)",
             color=FG, fontsize=16, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig("../img/04_feature_maps.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("Saved 04_feature_maps.png")
