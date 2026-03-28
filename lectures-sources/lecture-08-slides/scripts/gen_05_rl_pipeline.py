"""Slide: RL training pipeline — from real-world scan to trained agent."""
import matplotlib.pyplot as plt
import matplotlib.patches as patches

BG = "#1a1a2e"
FG = "white"

fig, ax = plt.subplots(figsize=(13, 5.5), facecolor=BG)
ax.set_facecolor(BG)
ax.set_xlim(-0.5, 13)
ax.set_ylim(-1, 6)
ax.axis("off")

# Top row: scan pipeline
top_steps = [
    (0.5, 4, 2.2, 1.2, "RGB-D скан\nабо SfM+MVS", "#3498db"),
    (3.5, 4, 2.2, 1.2, "Семантична\nанотація", "#2ecc71"),
    (6.5, 4, 2.2, 1.2, "3D-симулятор\n(Habitat / iGibson)", "#f39c12"),
]

for x, y, w, h, text, color in top_steps:
    rect = patches.FancyBboxPatch((x, y), w, h,
                                   boxstyle="round,pad=0.12", facecolor=color,
                                   edgecolor="white", linewidth=1.5, alpha=0.85)
    ax.add_patch(rect)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            color="white", fontsize=10, fontweight="bold", linespacing=1.2)

# Arrows between top steps
for i in range(len(top_steps) - 1):
    x1 = top_steps[i][0] + top_steps[i][2]
    x2 = top_steps[i + 1][0]
    y_mid = top_steps[i][1] + top_steps[i][3] / 2
    ax.annotate("", xy=(x2, y_mid), xytext=(x1 + 0.05, y_mid),
                arrowprops=dict(arrowstyle="->", color="white", lw=2))

# Bottom: RL training loop
rl_x, rl_y = 9.5, 2.5
rl_w, rl_h = 3.0, 2.8
rect_rl = patches.FancyBboxPatch((rl_x, rl_y), rl_w, rl_h,
                                  boxstyle="round,pad=0.15", facecolor="#9b59b6",
                                  edgecolor="white", linewidth=2, alpha=0.8)
ax.add_patch(rect_rl)
ax.text(rl_x + rl_w / 2, rl_y + rl_h * 0.78, "RL-агент", ha="center", va="center",
        color="white", fontsize=13, fontweight="bold")
ax.text(rl_x + rl_w / 2, rl_y + rl_h * 0.5, "спостереження → дія\n→ нагорода → навчання",
        ha="center", va="center", color="white", fontsize=8.5, alpha=0.9, linespacing=1.3)
ax.text(rl_x + rl_w / 2, rl_y + rl_h * 0.18, "PPO / SAC / DQN",
        ha="center", va="center", color="white", fontsize=8, alpha=0.7, style="italic")

# Arrow from simulator to RL
sim_x = top_steps[2][0] + top_steps[2][2] / 2
sim_y = top_steps[2][1]
ax.annotate("", xy=(rl_x + rl_w / 2, rl_y + rl_h),
            xytext=(sim_x, sim_y),
            arrowprops=dict(arrowstyle="->", color="#f39c12", lw=2.5,
                          connectionstyle="arc3,rad=-0.2"))
ax.text(9.2, 4.7, "RGB +\nглибина", color="#f39c12", fontsize=8, ha="center")

# RL loop back to simulator
ax.annotate("", xy=(top_steps[2][0] + top_steps[2][2], top_steps[2][1] + 0.2),
            xytext=(rl_x, rl_y + rl_h * 0.7),
            arrowprops=dict(arrowstyle="->", color="#9b59b6", lw=2,
                          connectionstyle="arc3,rad=0.3"))
ax.text(9.0, 3.5, "дія", color="#9b59b6", fontsize=9, fontweight="bold")

# Tasks list
tasks_x, tasks_y = 0.5, 0.3
ax.text(tasks_x, tasks_y + 2.2, "Типові задачі:", color=FG, fontsize=11, fontweight="bold")
tasks = [
    "Point-goal навігація — дістатися до координати",
    "Object-goal — знайти конкретний об'єкт",
    "Інструкції — «піди на кухню, знайди чашку»",
]
for i, task in enumerate(tasks):
    ax.text(tasks_x + 0.3, tasks_y + 1.6 - i * 0.55, f"• {task}",
            color=FG, fontsize=8.5, alpha=0.85)

# Game applications
ax.text(tasks_x, tasks_y - 0.5, "Ігрові застосування:", color="#2ecc71", fontsize=10, fontweight="bold")
game_apps = [
    "Тренування FPS-ботів на сканах реальних будівель",
    "Оцінка складності рівнів до художнього polish",
]
for i, app in enumerate(game_apps):
    ax.text(tasks_x + 0.3, tasks_y - 1.0 - i * 0.5, f"• {app}",
            color="#2ecc71", fontsize=8.5, alpha=0.85)

plt.suptitle("Від скану реального світу до тренованого RL-агента",
             color=FG, fontsize=14, fontweight="bold", y=0.99)
plt.tight_layout()
plt.savefig("../img/05_rl_pipeline.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("Saved 05_rl_pipeline.png")
