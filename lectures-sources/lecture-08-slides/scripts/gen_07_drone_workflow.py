"""Slide: Drone navigation — offline SfM map + real-time SLAM."""
import matplotlib.pyplot as plt
import matplotlib.patches as patches

BG = "#1a1a2e"
FG = "white"

fig, ax = plt.subplots(figsize=(12, 5), facecolor=BG)
ax.set_facecolor(BG)
ax.set_xlim(-0.5, 12)
ax.set_ylim(-0.5, 5.5)
ax.axis("off")

def draw_box(ax, x, y, w, h, text, color, fontsize=10, subtext=None):
    rect = patches.FancyBboxPatch((x, y), w, h,
                                   boxstyle="round,pad=0.12", facecolor=color,
                                   edgecolor="white", linewidth=1.5, alpha=0.85)
    ax.add_patch(rect)
    ty = y + h * 0.62 if subtext else y + h / 2
    ax.text(x + w / 2, ty, text, ha="center", va="center",
            color="white", fontsize=fontsize, fontweight="bold", linespacing=1.2)
    if subtext:
        ax.text(x + w / 2, y + h * 0.25, subtext, ha="center", va="center",
                color="white", fontsize=7.5, alpha=0.8, style="italic")

# Top row: Offline mapping
ax.text(0, 5.0, "ОФЛАЙН (до польоту)", color="#3498db", fontsize=12, fontweight="bold")
draw_box(ax, 0, 3.5, 2.3, 1.2, "Зйомка\nтериторії", "#3498db", 10)
draw_box(ax, 3.0, 3.5, 2.3, 1.2, "SfM + MVS", "#3498db", 10, "Pix4D / OpenDroneMap")
draw_box(ax, 6.0, 3.5, 2.8, 1.2, "3D-карта +\nортофотоплан", "#2c3e50", 10, "DSM, маршрути")

ax.annotate("", xy=(3.0, 4.1), xytext=(2.3 + 0.05, 4.1),
            arrowprops=dict(arrowstyle="->", color="white", lw=2))
ax.annotate("", xy=(6.0, 4.1), xytext=(5.3 + 0.05, 4.1),
            arrowprops=dict(arrowstyle="->", color="white", lw=2))

# Bottom row: Real-time flight
ax.text(0, 2.5, "РЕАЛЬНИЙ ЧАС (під час польоту)", color="#2ecc71", fontsize=12, fontweight="bold")
draw_box(ax, 0, 1.0, 2.3, 1.2, "Камера +\nIMU", "#2ecc71", 10)
draw_box(ax, 3.0, 1.0, 2.3, 1.2, "VIO / SLAM", "#2ecc71", 10, "ORB-SLAM3, VINS-Mono")
draw_box(ax, 6.0, 1.0, 2.8, 1.2, "Поточна поза\n(30+ Hz)", "#2ecc71", 10)

ax.annotate("", xy=(3.0, 1.6), xytext=(2.3 + 0.05, 1.6),
            arrowprops=dict(arrowstyle="->", color="white", lw=2))
ax.annotate("", xy=(6.0, 1.6), xytext=(5.3 + 0.05, 1.6),
            arrowprops=dict(arrowstyle="->", color="white", lw=2))

# Connection: offline map feeds into SLAM
ax.annotate("", xy=(4.15, 2.2), xytext=(7.0, 3.5),
            arrowprops=dict(arrowstyle="->", color="#f39c12", lw=2,
                          connectionstyle="arc3,rad=0.3", linestyle="--"))
ax.text(6.5, 2.9, "апріорна\nкарта", color="#f39c12", fontsize=8.5,
        fontweight="bold", ha="center")

# Navigation output
draw_box(ax, 9.5, 1.0, 2.2, 1.2, "Навігація\nта уникнення\nперешкод", "#e74c3c", 9)
ax.annotate("", xy=(9.5, 1.6), xytext=(8.8 + 0.05, 1.6),
            arrowprops=dict(arrowstyle="->", color="white", lw=2))

plt.suptitle("Навігація дронів: офлайн SfM + реальний час SLAM",
             color=FG, fontsize=14, fontweight="bold", y=0.99)
plt.tight_layout()
plt.savefig("../img/07_drone_workflow.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("Saved 07_drone_workflow.png")
