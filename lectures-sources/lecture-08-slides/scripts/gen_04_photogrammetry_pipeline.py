"""Slide: Photogrammetry-to-game pipeline — 5 steps as a flow diagram."""
import matplotlib.pyplot as plt
import matplotlib.patches as patches

BG = "#1a1a2e"
FG = "white"

steps = [
    ("Захоплення\nфото", "#3498db", "DSLR / дрон / телефон\n50-200 знімків"),
    ("SfM", "#2ecc71", "COLMAP / RealityCapture\n→ пози + розріджена хмара"),
    ("MVS", "#1abc9c", "Щільна реконструкція\n→ мільйони полігонів"),
    ("Обробка\nмешу", "#f39c12", "Ретопологія, UV,\nPBR-текстури"),
    ("Ігровий\nрушій", "#e74c3c", "UE5 / Unity\nколізії, LOD, освітлення"),
]

fig, ax = plt.subplots(figsize=(14, 4), facecolor=BG)
ax.set_facecolor(BG)
ax.set_xlim(-0.5, 14)
ax.set_ylim(-0.5, 3.5)
ax.axis("off")

box_w = 2.2
box_h = 1.5
y = 1.0
gap = 0.6

for i, (title, color, detail) in enumerate(steps):
    x = i * (box_w + gap)
    rect = patches.FancyBboxPatch((x, y), box_w, box_h,
                                   boxstyle="round,pad=0.15", facecolor=color,
                                   edgecolor="white", linewidth=1.5, alpha=0.85)
    ax.add_patch(rect)
    ax.text(x + box_w / 2, y + box_h * 0.65, title, ha="center", va="center",
            color="white", fontsize=11, fontweight="bold", linespacing=1.15)
    ax.text(x + box_w / 2, y + box_h * 0.22, detail, ha="center", va="center",
            color="white", fontsize=7.5, alpha=0.85, linespacing=1.2)

    if i < len(steps) - 1:
        ax.annotate("", xy=(x + box_w + gap * 0.15, y + box_h / 2),
                     xytext=(x + box_w + 0.05, y + box_h / 2),
                     arrowprops=dict(arrowstyle="->", color="white", lw=2))

# Labels
ax.text(0, 3.1, "Конвеєр фотограмметрії: від фотографій до ігрового рівня",
        color=FG, fontsize=14, fontweight="bold")

plt.tight_layout()
plt.savefig("../img/04_photogrammetry_pipeline.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("Saved 04_photogrammetry_pipeline.png")
