"""Slide: Vision Transformer — image patches to transformer."""
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

fig, ax = plt.subplots(figsize=(14, 5.5), facecolor=BG)
ax.set_facecolor(BG)
ax.set_xlim(-0.5, 16)
ax.set_ylim(-0.5, 7)
ax.set_aspect("equal")
ax.axis("off")

# Image with grid (patches)
img_x, img_y = 0.5, 1.5
patch_size = 0.8
grid = 4
colors_grid = plt.cm.viridis(np.linspace(0.2, 0.8, grid * grid))
np.random.shuffle(colors_grid)

for i in range(grid):
    for j in range(grid):
        rect = patches.Rectangle((img_x + j * patch_size, img_y + i * patch_size),
                                  patch_size, patch_size,
                                  facecolor=colors_grid[i * grid + j], edgecolor=FG,
                                  linewidth=0.5, alpha=0.6)
        ax.add_patch(rect)

ax.text(img_x + grid * patch_size / 2, img_y - 0.4, "Зображення\n(4×4 патчі)",
        ha="center", color=FG, fontsize=9)

# Arrow to embeddings
ax.annotate("", xy=(4.5, 3.1), xytext=(3.8, 3.1),
            arrowprops=dict(arrowstyle="->", color=GOLD, lw=2))

# Patch embeddings (vertical stack)
emb_x = 5
for i in range(6):
    y = 0.8 + i * 0.7
    color = ACCENT if i > 0 else GOLD
    label = f"P{i}" if i > 0 else "[CLS]"
    rect = patches.FancyBboxPatch((emb_x, y), 1.2, 0.55,
        boxstyle="round,pad=0.05", facecolor=color, alpha=0.5, edgecolor=FG, linewidth=0.8)
    ax.add_patch(rect)
    ax.text(emb_x + 0.6, y + 0.27, label, ha="center", va="center", color=FG, fontsize=7)

ax.text(emb_x + 0.6, 5.5, "...", ha="center", color=FG, fontsize=14)
ax.text(emb_x + 0.6, 0.3, "Embeddings\n+ позиції", ha="center", color=FG, fontsize=8, alpha=0.7)

# Arrow to transformer
ax.annotate("", xy=(7.2, 3.1), xytext=(6.5, 3.1),
            arrowprops=dict(arrowstyle="->", color=GOLD, lw=2))

# Transformer block (repeated)
for i in range(3):
    tx = 7.5 + i * 2
    block = patches.FancyBboxPatch((tx, 1.5), 1.5, 3.2,
        boxstyle="round,pad=0.15", facecolor=PURPLE, alpha=0.4 + i * 0.1,
        edgecolor=FG, linewidth=1.5)
    ax.add_patch(block)

    # Self-attention label
    ax.text(tx + 0.75, 3.8, "Self-\nAttention", ha="center", va="center",
            color=FG, fontsize=7, fontweight="bold")
    # FFN label
    ax.text(tx + 0.75, 2.2, "FFN", ha="center", va="center",
            color=FG, fontsize=8, fontweight="bold")
    # Divider
    ax.plot([tx + 0.15, tx + 1.35], [3.0, 3.0], "-", color=FG, alpha=0.3, linewidth=0.5)

    if i < 2:
        ax.annotate("", xy=(tx + 2, 3.1), xytext=(tx + 1.5, 3.1),
                    arrowprops=dict(arrowstyle="->", color=GOLD, lw=1.5))

ax.text(9.5, 0.7, "Transformer Encoder (×L)", ha="center", color=PURPLE, fontsize=10, fontweight="bold")

# Arrow to output
ax.annotate("", xy=(14.0, 3.1), xytext=(13.2, 3.1),
            arrowprops=dict(arrowstyle="->", color=GOLD, lw=2))

# Output
output_box = patches.FancyBboxPatch((14.2, 2.0), 1.5, 2.2,
    boxstyle="round,pad=0.15", facecolor=ACCENT2, alpha=0.5, edgecolor=FG, linewidth=1.5)
ax.add_patch(output_box)
ax.text(14.95, 3.1, "Клас /\nМаска /\nРамки", ha="center", va="center",
        color=FG, fontsize=9, fontweight="bold")

# Title annotations
ax.text(2, 6.5, "1. Розрізати", color=GOLD, fontsize=10, fontweight="bold", ha="center")
ax.text(5.6, 6.5, "2. Embedding", color=ACCENT, fontsize=10, fontweight="bold", ha="center")
ax.text(9.5, 6.5, "3. Self-Attention", color=PURPLE, fontsize=10, fontweight="bold", ha="center")
ax.text(14.95, 6.5, "4. Вихід", color=ACCENT2, fontsize=10, fontweight="bold", ha="center")

plt.suptitle("Vision Transformer (ViT): зображення → патчі → Transformer",
             color=FG, fontsize=15, fontweight="bold", y=0.98)
plt.tight_layout()
plt.savefig("../img/05_vit_architecture.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("Saved 05_vit_architecture.png")
