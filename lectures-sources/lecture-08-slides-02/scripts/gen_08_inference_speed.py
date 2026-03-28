"""Slide: Inference speed comparison — what runs in real-time for games."""
import matplotlib.pyplot as plt
import numpy as np

BG = "#1a1a2e"
FG = "white"
ACCENT = "#3498db"
ACCENT2 = "#2ecc71"
WARN = "#e74c3c"
GOLD = "#f39c12"
PURPLE = "#9b59b6"

fig, ax = plt.subplots(figsize=(14, 6), facecolor=BG)
ax.set_facecolor(BG)

models = [
    "YOLOv8-nano",
    "Depth Anything v2 (S)",
    "CLIP ViT-B/32",
    "MobileNet + DeepLab",
    "YOLOv8-large",
    "SAM (ViT-H)",
    "Swin-L + Mask R-CNN",
]
times_gpu = [1.2, 3, 4, 4, 5.8, 50, 65]
colors = [ACCENT2, ACCENT2, GOLD, ACCENT2, GOLD, WARN, WARN]

y_pos = np.arange(len(models))[::-1]

bars = ax.barh(y_pos, times_gpu, height=0.6, color=colors, alpha=0.7, edgecolor=FG, linewidth=0.5)

# Value labels
for bar, val in zip(bars, times_gpu):
    ax.text(bar.get_width() + 1.5, bar.get_y() + bar.get_height()/2,
            f"{val} мс", va="center", color=FG, fontsize=11, fontweight="bold")

ax.set_yticks(y_pos)
ax.set_yticklabels(models, color=FG, fontsize=11)
ax.set_xlabel("Час інференсу (мс, GPU)", color=FG, fontsize=12)

# 16.7ms line (60 FPS budget)
ax.axvline(x=16.7, color=GOLD, linewidth=2, linestyle="--", alpha=0.8)
ax.text(17.5, len(models) - 0.5, "60 FPS\n(16.7 мс)", color=GOLD, fontsize=10, fontweight="bold")

# Style
ax.tick_params(colors=FG)
ax.spines["bottom"].set_color("#4a6fa5")
ax.spines["left"].set_color("#4a6fa5")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.set_xlim(0, 80)

# Legend
ax.text(55, 6.2, "● Реалтайм у грі", color=ACCENT2, fontsize=10, fontweight="bold")
ax.text(55, 5.6, "● Умовно реалтайм", color=GOLD, fontsize=10, fontweight="bold")
ax.text(55, 5.0, "● Лише офлайн", color=WARN, fontsize=10, fontweight="bold")

plt.suptitle("Швидкість інференсу: що працює в реальному часі?",
             color=FG, fontsize=15, fontweight="bold", y=0.98)
plt.tight_layout()
plt.savefig("../img/08_inference_speed.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("Saved 08_inference_speed.png")
