"""Slide: The X problem — same object, different pixel matrices when shifted."""
import numpy as np
import matplotlib.pyplot as plt

BG = "#1a1a2e"
FG = "white"

def make_x(size=7, r0=0, c0=0):
    """Binary X pattern with 1 on diagonals, -1 elsewhere."""
    m = np.full((size, size), -1, dtype=float)
    for i in range(size):
        ri, ci1, ci2 = i + r0, i + c0, (size - 1 - i) + c0
        if 0 <= ri < size:
            if 0 <= ci1 < size:
                m[ri, ci1] = 1
            if 0 <= ci2 < size:
                m[ri, ci2] = 1
    return m

x1 = make_x(r0=0, c0=0)
x2 = make_x(r0=1, c0=1)

fig, axes = plt.subplots(2, 3, figsize=(13, 7), facecolor=BG,
                         gridspec_kw={"width_ratios": [1, 0.15, 1]})

def draw_matrix(ax, mat, title, highlight_pos=None):
    cmap = plt.cm.RdYlGn
    ax.imshow(mat, cmap=cmap, vmin=-1.5, vmax=1.5)
    ax.set_title(title, color=FG, fontsize=13, pad=6)
    n = mat.shape[0]
    for i in range(n):
        for j in range(n):
            v = int(mat[i, j])
            col = "black" if mat[i, j] > 0 else FG
            ax.text(j, i, f"{v:+d}", ha="center", va="center",
                    fontsize=11, color=col, fontweight="bold")
    if highlight_pos:
        for (ri, ci) in highlight_pos:
            rect = plt.Rectangle((ci - 0.5, ri - 0.5), 1, 1,
                                  linewidth=2, edgecolor="#e74c3c", facecolor="none")
            ax.add_patch(rect)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_facecolor(BG)

# Row 0: visual X images
for row, (mat, label) in enumerate([(x1, "X (вихідний)"), (x2, "X (зміщений)")]):
    ax_img = axes[row][0]
    ax_img.imshow((mat + 1) / 2, cmap="gray", vmin=0, vmax=1)
    ax_img.set_title(label, color=FG, fontsize=14, pad=6)
    ax_img.axis("off")
    ax_img.set_facecolor(BG)

    ax_mid = axes[row][1]
    ax_mid.text(0.5, 0.5, "→", ha="center", va="center",
                fontsize=28, color=FG, transform=ax_mid.transAxes)
    ax_mid.axis("off")
    ax_mid.set_facecolor(BG)

    ax_num = axes[row][2]
    draw_matrix(ax_num, mat, f"Числова матриця ({label})")

# Red "≠" between the two rows
fig.text(0.5, 0.52, "≠  (різні числа!)", ha="center", va="center",
         fontsize=22, color="#e74c3c", fontweight="bold")

plt.suptitle("Один і той самий X — різні числові матриці при зсуві",
             color=FG, fontsize=16, fontweight="bold", y=1.01)
plt.tight_layout()
plt.savefig("../img/02_x_case.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("Saved 02_x_case.png")
