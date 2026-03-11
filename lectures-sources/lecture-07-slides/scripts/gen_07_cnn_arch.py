"""Slide: CNN Architecture block diagram — Input→Conv+ReLU→Pool→...→Softmax."""
import matplotlib.pyplot as plt
import matplotlib.patches as patches

BG = "#1a1a2e"
FG = "white"

blocks = [
    ("Вхідне\nзображення\n3×H×W",    "#34495e", "white"),
    ("Conv2D\n+ ReLU",                "#2980b9", "white"),
    ("MaxPool\n2×2",                  "#1a5276", "white"),
    ("Conv2D\n+ ReLU",                "#2980b9", "white"),
    ("MaxPool\n2×2",                  "#1a5276", "white"),
    ("Flatten",                       "#6c3483", "white"),
    ("Linear\n+ ReLU",               "#8e44ad", "white"),
    ("Softmax\n→ клас",               "#117a65", "white"),
]

fig, ax = plt.subplots(figsize=(16, 5), facecolor=BG)
ax.set_facecolor(BG)
ax.set_xlim(-0.5, len(blocks) + 0.5)
ax.set_ylim(-1.5, 2.5)
ax.axis("off")

box_w, box_h = 1.55, 1.7
gap = 0.3
x = 0.1

positions = []
for i, (label, color, tcolor) in enumerate(blocks):
    bx = x + i * (box_w + gap)
    positions.append(bx + box_w / 2)
    rect = patches.FancyBboxPatch(
        (bx, -box_h / 2), box_w, box_h,
        boxstyle="round,pad=0.08",
        facecolor=color, edgecolor=FG, linewidth=1.5, alpha=0.92
    )
    ax.add_patch(rect)
    ax.text(bx + box_w / 2, 0, label, ha="center", va="center",
            fontsize=11, color=tcolor, fontweight="bold", multialignment="center")

# Arrows
for i in range(len(positions) - 1):
    x0 = x + i * (box_w + gap) + box_w
    x1 = x0 + gap
    ax.annotate("", xy=(x1, 0), xytext=(x0, 0),
                arrowprops=dict(arrowstyle="->", color=FG, lw=2.0))

# Bracket labels
def brace_label(ax, x0, x1, y, label, color):
    ax.annotate("", xy=(x1, y), xytext=(x0, y),
                arrowprops=dict(arrowstyle="<->", color=color, lw=1.5))
    ax.text((x0 + x1) / 2, y - 0.28, label, ha="center", va="top",
            fontsize=11, color=color, fontweight="bold")

# Feature learning bracket (conv+pool blocks)
brace_label(ax,
            x + (box_w + gap),          # after input
            x + 4 * (box_w + gap) + box_w,  # after 4th block (2nd pool)
            -1.15, "⬆ Виділення ознак (Feature Learning)", "#3498db")

# Classification bracket
brace_label(ax,
            x + 5 * (box_w + gap),       # flatten
            x + 7 * (box_w + gap) + box_w,  # softmax
            -1.15, "⬆ Класифікація", "#2ecc71")

plt.suptitle("Архітектура CNN для класифікації зображень",
             color=FG, fontsize=17, fontweight="bold", y=1.01)
plt.tight_layout()
plt.savefig("../img/07_cnn_arch.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("Saved 07_cnn_arch.png")
