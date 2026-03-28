"""Slide: CLIP — shared embedding space for images and text."""
import matplotlib.pyplot as plt
import matplotlib.patches as patches

BG = "#1a1a2e"
FG = "white"
ACCENT = "#3498db"
ACCENT2 = "#2ecc71"
WARN = "#e74c3c"
GOLD = "#f39c12"
PURPLE = "#9b59b6"

fig, ax = plt.subplots(figsize=(14, 6), facecolor=BG)
ax.set_facecolor(BG)
ax.set_xlim(-1, 15)
ax.set_ylim(-1, 8)
ax.set_aspect("equal")
ax.axis("off")

# Image encoder (left)
img_box = patches.FancyBboxPatch((0, 4), 3, 2.5,
    boxstyle="round,pad=0.2", facecolor=ACCENT, alpha=0.4, edgecolor=FG, linewidth=1.5)
ax.add_patch(img_box)
ax.text(1.5, 5.25, "Image\nEncoder\n(ViT)", ha="center", va="center",
        color=FG, fontsize=11, fontweight="bold")
ax.text(1.5, 3.5, "Зображення", ha="center", color=ACCENT, fontsize=10)

# Text encoder (left)
txt_box = patches.FancyBboxPatch((0, 0.5), 3, 2.5,
    boxstyle="round,pad=0.2", facecolor=ACCENT2, alpha=0.4, edgecolor=FG, linewidth=1.5)
ax.add_patch(txt_box)
ax.text(1.5, 1.75, "Text\nEncoder\n(Transformer)", ha="center", va="center",
        color=FG, fontsize=11, fontweight="bold")
ax.text(1.5, 0.0, "Текст", ha="center", color=ACCENT2, fontsize=10)

# Arrows to shared space
ax.annotate("", xy=(5, 5.0), xytext=(3.2, 5.25),
            arrowprops=dict(arrowstyle="->", color=ACCENT, lw=2))
ax.annotate("", xy=(5, 2.5), xytext=(3.2, 1.75),
            arrowprops=dict(arrowstyle="->", color=ACCENT2, lw=2))

# Shared embedding space (center circle)
circle = plt.Circle((7.5, 3.75), 2.8, facecolor=PURPLE, alpha=0.15, edgecolor=GOLD, linewidth=2, linestyle="--")
ax.add_patch(circle)
ax.text(7.5, 7.0, "Спільний embedding-простір", ha="center", color=GOLD,
        fontsize=12, fontweight="bold")

# Points in shared space
# Matching pairs close together
pairs = [
    (6.5, 4.8, "IMG", "\"sword\"", WARN),
    (8.0, 3.0, "IMG", "\"shield\"", ACCENT),
    (7.8, 4.5, "IMG", "\"castle\"", ACCENT2),
]

for px, py, emoji, text, color in pairs:
    ax.plot(px, py, "o", color=color, markersize=12, zorder=5)
    ax.text(px + 0.15, py + 0.3, "[img]", fontsize=8, ha="center", color=color, alpha=0.7)
    ax.plot(px + 0.7, py - 0.3, "s", color=color, markersize=10, zorder=5, alpha=0.7)
    ax.text(px + 0.7, py - 0.6, text, fontsize=9, ha="center", color=color, fontweight="bold")

# Right side: applications
app_x = 11.5
apps = [
    (5.8, "Zero-shot\nкласифікація", WARN),
    (4.0, "Семантичний\nпошук ассетів", ACCENT),
    (2.2, "Генерація\nз тексту", ACCENT2),
]

ax.annotate("", xy=(10.5, 3.75), xytext=(10.0, 3.75),
            arrowprops=dict(arrowstyle="->", color=GOLD, lw=2))

for y, label, color in apps:
    box = patches.FancyBboxPatch((app_x - 0.5, y - 0.5), 3.5, 1.2,
        boxstyle="round,pad=0.15", facecolor=color, alpha=0.2, edgecolor=color, linewidth=1.5)
    ax.add_patch(box)
    ax.text(app_x + 1.25, y + 0.1, label, ha="center", va="center",
            color=FG, fontsize=10, fontweight="bold")

plt.suptitle("CLIP: зір + мова = спільний простір розуміння",
             color=FG, fontsize=15, fontweight="bold", y=0.98)
plt.tight_layout()
plt.savefig("../img/06_clip_concept.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("Saved 06_clip_concept.png")
