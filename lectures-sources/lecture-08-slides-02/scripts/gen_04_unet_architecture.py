"""Slide: U-Net architecture — encoder-decoder with skip connections."""
import matplotlib.pyplot as plt
import matplotlib.patches as patches

BG = "#1a1a2e"
FG = "white"
ACCENT = "#3498db"
ACCENT2 = "#2ecc71"
WARN = "#e74c3c"
GOLD = "#f39c12"

fig, ax = plt.subplots(figsize=(14, 6), facecolor=BG)
ax.set_facecolor(BG)
ax.set_xlim(-1, 15)
ax.set_ylim(-0.5, 8)
ax.set_aspect("equal")
ax.axis("off")

# Encoder blocks (left side, going down)
enc_blocks = [
    (1, 6.5, 1.5, 1.0, "64", ACCENT),
    (3, 5.0, 1.5, 1.2, "128", ACCENT),
    (5, 3.2, 1.5, 1.4, "256", ACCENT),
    (7, 1.2, 1.5, 1.6, "512", "#2471a3"),
]

# Decoder blocks (right side, going up)
dec_blocks = [
    (9, 3.2, 1.5, 1.4, "256", ACCENT2),
    (11, 5.0, 1.5, 1.2, "128", ACCENT2),
    (13, 6.5, 1.5, 1.0, "64", ACCENT2),
]

# Bottleneck
bn_x, bn_y, bn_w, bn_h = 7, 1.2, 1.5, 1.6
bottleneck = patches.FancyBboxPatch((bn_x - bn_w/2, bn_y - bn_h/2), bn_w, bn_h,
    boxstyle="round,pad=0.1", facecolor="#2471a3", edgecolor=FG, linewidth=1.5, alpha=0.8)
ax.add_patch(bottleneck)
ax.text(bn_x, bn_y, "512", ha="center", va="center", color=FG, fontsize=10, fontweight="bold")
ax.text(bn_x, bn_y - bn_h/2 - 0.3, "Bottleneck", ha="center", color=GOLD, fontsize=9)

# Draw encoder
for x, y, w, h, label, color in enc_blocks[:-1]:
    rect = patches.FancyBboxPatch((x - w/2, y - h/2), w, h,
        boxstyle="round,pad=0.1", facecolor=color, edgecolor=FG, linewidth=1.5, alpha=0.7)
    ax.add_patch(rect)
    ax.text(x, y, label, ha="center", va="center", color=FG, fontsize=10, fontweight="bold")

# Down arrows (encoder)
for i in range(len(enc_blocks) - 1):
    x1, y1 = enc_blocks[i][0], enc_blocks[i][1] - enc_blocks[i][3]/2
    x2, y2 = enc_blocks[i+1][0], enc_blocks[i+1][1] + enc_blocks[i+1][3]/2
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", color=ACCENT, lw=2))

# Draw decoder
for x, y, w, h, label, color in dec_blocks:
    rect = patches.FancyBboxPatch((x - w/2, y - h/2), w, h,
        boxstyle="round,pad=0.1", facecolor=color, edgecolor=FG, linewidth=1.5, alpha=0.7)
    ax.add_patch(rect)
    ax.text(x, y, label, ha="center", va="center", color=FG, fontsize=10, fontweight="bold")

# Up arrows (decoder)
# Bottleneck to first decoder
ax.annotate("", xy=(dec_blocks[0][0], dec_blocks[0][1] - dec_blocks[0][3]/2),
            xytext=(bn_x, bn_y + bn_h/2),
            arrowprops=dict(arrowstyle="->", color=ACCENT2, lw=2))

for i in range(len(dec_blocks) - 1):
    x1, y1 = dec_blocks[i][0], dec_blocks[i][1] + dec_blocks[i][3]/2
    x2, y2 = dec_blocks[i+1][0], dec_blocks[i+1][1] - dec_blocks[i+1][3]/2
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", color=ACCENT2, lw=2))

# Skip connections
skip_pairs = [
    (enc_blocks[0], dec_blocks[2]),  # 64 -> 64
    (enc_blocks[1], dec_blocks[1]),  # 128 -> 128
    (enc_blocks[2], dec_blocks[0]),  # 256 -> 256
]

for (ex, ey, ew, eh, _, _), (dx, dy, dw, dh, _, _) in skip_pairs:
    ax.annotate("", xy=(dx - dw/2, dy), xytext=(ex + ew/2, ey),
                arrowprops=dict(arrowstyle="->", color=GOLD, lw=2, linestyle="--", alpha=0.8,
                               connectionstyle="arc3,rad=-0.2"))

# Labels
ax.text(2, 7.8, "Encoder (↓)", color=ACCENT, fontsize=12, fontweight="bold", ha="center")
ax.text(12, 7.8, "Decoder (↑)", color=ACCENT2, fontsize=12, fontweight="bold", ha="center")
ax.text(7.5, 7.8, "Skip connections", color=GOLD, fontsize=11, fontweight="bold", ha="center")

# Input/Output labels
ax.text(1, 7.5, "Вхід\n(зображення)", ha="center", color=FG, fontsize=9, alpha=0.7)
ax.text(13, 7.5, "Вихід\n(маска)", ha="center", color=FG, fontsize=9, alpha=0.7)

plt.suptitle("U-Net: encoder-decoder з skip connections",
             color=FG, fontsize=15, fontweight="bold", y=0.98)
plt.tight_layout()
plt.savefig("../img/04_unet_architecture.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("Saved 04_unet_architecture.png")
