"""Slide: Hybrid workflow — SfM for structure + 3DGS for appearance."""
import matplotlib.pyplot as plt
import matplotlib.patches as patches

BG = "#1a1a2e"
FG = "white"

fig, ax = plt.subplots(figsize=(12, 5.5), facecolor=BG)
ax.set_facecolor(BG)
ax.set_xlim(-0.5, 12)
ax.set_ylim(-0.5, 6)
ax.axis("off")

def draw_box(ax, x, y, w, h, text, color, fontsize=10, subtext=None):
    rect = patches.FancyBboxPatch((x, y), w, h,
                                   boxstyle="round,pad=0.12", facecolor=color,
                                   edgecolor="white", linewidth=1.5, alpha=0.85)
    ax.add_patch(rect)
    ty = y + h * 0.6 if subtext else y + h / 2
    ax.text(x + w / 2, ty, text, ha="center", va="center",
            color="white", fontsize=fontsize, fontweight="bold", linespacing=1.2)
    if subtext:
        ax.text(x + w / 2, y + h * 0.25, subtext, ha="center", va="center",
                color="white", fontsize=7.5, alpha=0.8, style="italic")

# Input
draw_box(ax, 0, 3.5, 2.5, 1.2, "Фото / відео\nз телефону", "#7f8c8d", 10)

# SfM
draw_box(ax, 3.5, 3.5, 2.5, 1.2, "COLMAP /\nRealityCapture", "#3498db", 10, "SfM → пози камер")

# Arrow: input -> SfM
ax.annotate("", xy=(3.5, 4.1), xytext=(2.5 + 0.05, 4.1),
            arrowprops=dict(arrowstyle="->", color="white", lw=2))

# Branch 1: Dense mesh (top)
draw_box(ax, 7, 4.8, 2.5, 1.0, "COLMAP Dense /\nOpenMVS", "#2ecc71", 9, "→ полігональний меш")

# Branch 2: 3DGS (bottom)
draw_box(ax, 7, 2.5, 2.5, 1.0, "Nerfstudio /\nPostShot", "#9b59b6", 9, "→ 3D Gaussian Splatting")

# Arrows from SfM to branches
ax.annotate("", xy=(7, 5.3), xytext=(6.0, 4.3),
            arrowprops=dict(arrowstyle="->", color="#2ecc71", lw=2,
                          connectionstyle="arc3,rad=-0.2"))
ax.annotate("", xy=(7, 3.0), xytext=(6.0, 3.9),
            arrowprops=dict(arrowstyle="->", color="#9b59b6", lw=2,
                          connectionstyle="arc3,rad=0.2"))

# Labels on branches
ax.text(6.5, 5.0, "геометрія", color="#2ecc71", fontsize=8, fontweight="bold", rotation=25)
ax.text(6.5, 3.2, "вигляд", color="#9b59b6", fontsize=8, fontweight="bold", rotation=-25)

# UE5 convergence
draw_box(ax, 10, 3.3, 1.8, 1.5, "Unreal\nEngine 5", "#e74c3c", 11)

# Arrows to UE5
ax.annotate("", xy=(10, 4.1), xytext=(9.5 + 0.05, 5.0),
            arrowprops=dict(arrowstyle="->", color="#2ecc71", lw=2,
                          connectionstyle="arc3,rad=0.15"))
ax.annotate("", xy=(10, 3.9), xytext=(9.5 + 0.05, 3.2),
            arrowprops=dict(arrowstyle="->", color="#9b59b6", lw=2,
                          connectionstyle="arc3,rad=-0.15"))

# Labels for what each branch provides
ax.text(9.8, 5.0, "колізії,\nфізика, LOD", color="#2ecc71", fontsize=7.5, ha="right")
ax.text(9.8, 2.5, "фотореалістичний\nфон (90+ FPS)", color="#9b59b6", fontsize=7.5, ha="right")

# Bottom note
ax.text(6, 0.5, "SfM дає структуру (скелет) • Нейронні методи дають зовнішній вигляд",
        ha="center", va="center", color=FG, fontsize=10,
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#2c3e50", edgecolor="#4a4a7a", alpha=0.8))

plt.suptitle("Гібридний конвеєр: класичний SfM + нейронні методи",
             color=FG, fontsize=14, fontweight="bold", y=0.98)
plt.tight_layout()
plt.savefig("../img/06_hybrid_workflow.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("Saved 06_hybrid_workflow.png")
