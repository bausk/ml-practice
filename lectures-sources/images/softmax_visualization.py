"""
Visualization of Softmax function for multiclass classification
Shows how Softmax converts raw scores (logits) into probabilities
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import seaborn as sns

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

def softmax(z):
    """Compute softmax values for each set of scores in z."""
    exp_z = np.exp(z - np.max(z))  # Subtract max for numerical stability
    return exp_z / exp_z.sum()

# ============================================================================
# Figure 1: Basic Softmax Transformation (3 classes)
# ============================================================================
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

# Example 1: Clear winner
scores_1 = np.array([2.0, 1.0, 0.1])
probs_1 = softmax(scores_1)

# Example 2: Close competition
scores_2 = np.array([1.5, 1.3, 1.2])
probs_2 = softmax(scores_2)

# Example 3: Very confident
scores_3 = np.array([5.0, -2.0, -3.0])
probs_3 = softmax(scores_3)

examples = [
    (scores_1, probs_1, "Клас 1 переможець\n(помірна впевненість)"),
    (scores_2, probs_2, "Конкуренція між класами\n(низька впевненість)"),
    (scores_3, probs_3, "Дуже впевнене передбачення\n(висока впевненість)")
]

class_names = ['Casual', 'Hardcore', 'Social']
colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']

for idx, (ax, (scores, probs, title)) in enumerate(zip(axes, examples)):
    x = np.arange(len(class_names))
    width = 0.35

    # Raw scores
    bars1 = ax.bar(x - width/2, scores, width, label='Сирі скори (logits)',
                   alpha=0.8, edgecolor='black', linewidth=1.5)

    # Probabilities
    bars2 = ax.bar(x + width/2, probs, width, label='Ймовірності (softmax)',
                   alpha=0.8, edgecolor='black', linewidth=1.5)

    # Color bars
    for i, (bar1, bar2) in enumerate(zip(bars1, bars2)):
        bar1.set_color(colors[i])
        bar1.set_alpha(0.5)
        bar2.set_color(colors[i])

    # Add value labels on bars
    for i, (score, prob) in enumerate(zip(scores, probs)):
        ax.text(i - width/2, score + 0.1, f'{score:.1f}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
        ax.text(i + width/2, prob + 0.02, f'{prob:.2f}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax.set_ylabel('Значення', fontsize=12)
    ax.set_title(title, fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(class_names)
    ax.legend(loc='upper right', fontsize=9)
    ax.grid(axis='y', alpha=0.3)

    # Add sum annotation for probabilities
    prob_sum = probs.sum()
    ax.text(0.98, 0.98, f'Σ prob = {prob_sum:.3f}',
            transform=ax.transAxes, fontsize=10,
            verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig('softmax_basic_transformation.png', dpi=150, bbox_inches='tight')
print("✓ Saved: softmax_basic_transformation.png")
plt.close()

# ============================================================================
# Figure 2: Temperature Effect on Softmax
# ============================================================================
fig, axes = plt.subplots(2, 3, figsize=(16, 10))

# Original scores
scores = np.array([3.0, 1.0, 0.5])
temperatures = [0.5, 1.0, 2.0, 5.0, 10.0, 100.0]

for idx, (ax, T) in enumerate(zip(axes.flat, temperatures)):
    # Apply temperature scaling
    scaled_scores = scores / T
    probs = softmax(scaled_scores)

    # Create bar plot
    bars = ax.bar(class_names, probs, color=colors, alpha=0.8,
                  edgecolor='black', linewidth=2)

    # Add value labels
    for i, (bar, prob) in enumerate(zip(bars, probs)):
        ax.text(i, prob + 0.02, f'{prob:.3f}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')

    ax.set_ylabel('Ймовірність', fontsize=12)
    subtitle = "(гостріший розподіл)" if T < 1 else "(м'якший розподіл)" if T > 1 else "(стандартний)"
    ax.set_title(f'Temperature = {T}\n{subtitle}',
                 fontsize=12, fontweight='bold')
    ax.set_ylim(0, 1.1)
    ax.grid(axis='y', alpha=0.3)

    # Add entropy measure
    entropy = -np.sum(probs * np.log(probs + 1e-10))
    max_entropy = np.log(len(probs))
    ax.text(0.98, 0.98, f'Ентропія: {entropy:.2f}/{max_entropy:.2f}',
            transform=ax.transAxes, fontsize=9,
            verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))

plt.suptitle('Вплив температури на Softmax\nСирі скори: [3.0, 1.0, 0.5]',
             fontsize=15, fontweight='bold', y=1.00)
plt.tight_layout()
plt.savefig('softmax_temperature_effect.png', dpi=150, bbox_inches='tight')
print("✓ Saved: softmax_temperature_effect.png")
plt.close()

# ============================================================================
# Figure 3: Softmax vs Argmax vs One-Hot
# ============================================================================
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

scores = np.array([2.5, 1.8, 0.3, -0.5])
class_names_4 = ['FPS', 'RPG', 'Strategy', 'Puzzle']
colors_4 = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#95E1D3']

# Softmax probabilities
probs = softmax(scores)

# Argmax (hard classification)
argmax_output = np.zeros_like(scores)
argmax_output[np.argmax(scores)] = 1.0

# One-hot encoding (ground truth example)
true_label = 1  # RPG is the true class
one_hot = np.zeros_like(scores)
one_hot[true_label] = 1.0

outputs = [
    (scores, "Сирі скори (logits)", "Вихід нейронної мережі"),
    (probs, "Softmax ймовірності", "Навчання з крос-ентропією"),
    (argmax_output, "Argmax (жорстке рішення)", "Тестування/інференс")
]

for ax, (values, title, subtitle) in zip(axes, outputs):
    bars = ax.bar(class_names_4, values, color=colors_4, alpha=0.8,
                  edgecolor='black', linewidth=2)

    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, values)):
        if val > 0.01:  # Only show non-zero values
            ax.text(i, val + 0.05, f'{val:.2f}',
                    ha='center', va='bottom', fontsize=11, fontweight='bold')

    ax.set_ylabel('Значення', fontsize=12)
    ax.set_title(f'{title}\n{subtitle}', fontsize=12, fontweight='bold')
    ax.set_ylim(0, max(scores.max(), 1.0) + 0.3)
    ax.grid(axis='y', alpha=0.3)

# Add ground truth comparison
axes[1].axhline(y=one_hot[true_label], color='green', linestyle='--',
                linewidth=2, label=f'Ground truth: {class_names_4[true_label]}')
axes[1].legend(loc='upper right', fontsize=10)

plt.tight_layout()
plt.savefig('softmax_vs_argmax.png', dpi=150, bbox_inches='tight')
print("✓ Saved: softmax_vs_argmax.png")
plt.close()

# ============================================================================
# Figure 4: Softmax Computation Flow (Step-by-Step)
# ============================================================================
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Покрокове обчислення Softmax', fontsize=16, fontweight='bold')

scores = np.array([2.0, 1.0, 0.1])
class_names_3 = ['Клас 1', 'Клас 2', 'Клас 3']

# Step 1: Raw scores
ax = axes[0, 0]
bars = ax.bar(class_names_3, scores, color=colors, alpha=0.8,
              edgecolor='black', linewidth=2)
for i, val in enumerate(scores):
    ax.text(i, val + 0.1, f'{val:.1f}', ha='center', va='bottom',
            fontsize=12, fontweight='bold')
ax.set_ylabel('z (logits)', fontsize=12)
ax.set_title('Крок 1: Сирі скори\nz = [2.0, 1.0, 0.1]', fontsize=12, fontweight='bold')
ax.grid(axis='y', alpha=0.3)

# Step 2: Exponentiation
exp_scores = np.exp(scores)
ax = axes[0, 1]
bars = ax.bar(class_names_3, exp_scores, color=colors, alpha=0.8,
              edgecolor='black', linewidth=2)
for i, val in enumerate(exp_scores):
    ax.text(i, val + 0.3, f'{val:.2f}', ha='center', va='bottom',
            fontsize=12, fontweight='bold')
ax.set_ylabel('exp(z)', fontsize=12)
ax.set_title(f'Крок 2: Експонента\nexp(z) = [{exp_scores[0]:.2f}, {exp_scores[1]:.2f}, {exp_scores[2]:.2f}]',
             fontsize=12, fontweight='bold')
ax.grid(axis='y', alpha=0.3)

# Step 3: Sum
exp_sum = exp_scores.sum()
ax = axes[1, 0]
ax.bar(['Сума'], [exp_sum], color='orange', alpha=0.8,
       edgecolor='black', linewidth=2)
ax.text(0, exp_sum + 0.3, f'{exp_sum:.2f}', ha='center', va='bottom',
        fontsize=14, fontweight='bold')
ax.set_ylabel('Σ exp(z)', fontsize=12)
ax.set_title(f'Крок 3: Сума експонент\nΣ = {exp_sum:.2f}',
             fontsize=12, fontweight='bold')
ax.set_ylim(0, exp_sum + 1)
ax.grid(axis='y', alpha=0.3)

# Step 4: Normalization (Softmax)
probs = softmax(scores)
ax = axes[1, 1]
bars = ax.bar(class_names_3, probs, color=colors, alpha=0.8,
              edgecolor='black', linewidth=2)
for i, val in enumerate(probs):
    ax.text(i, val + 0.02, f'{val:.3f}', ha='center', va='bottom',
            fontsize=12, fontweight='bold')
ax.set_ylabel('P(y=k|x)', fontsize=12)
ax.set_title(f'Крок 4: Нормалізація\nP(y) = exp(z) / Σ = [{probs[0]:.3f}, {probs[1]:.3f}, {probs[2]:.3f}]',
             fontsize=12, fontweight='bold')
ax.set_ylim(0, 1.1)
ax.grid(axis='y', alpha=0.3)

# Add formula annotation
formula_text = r'$P(y = k | \mathbf{x}) = \frac{e^{z_k}}{\sum_{j=1}^{K} e^{z_j}}$'
fig.text(0.5, 0.02, formula_text, ha='center', fontsize=16,
         bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

plt.tight_layout(rect=[0, 0.04, 1, 0.96])
plt.savefig('softmax_computation_steps.png', dpi=150, bbox_inches='tight')
print("✓ Saved: softmax_computation_steps.png")
plt.close()

# ============================================================================
# Figure 5: Game Example - Genre Classification
# ============================================================================
fig, axes = plt.subplots(2, 2, figsize=(15, 12))
fig.suptitle('Приклад з ігор: Класифікація жанру гри за описом',
             fontsize=16, fontweight='bold')

genres = ['FPS', 'RPG', 'Strategy', 'Racing', 'Puzzle']
colors_5 = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#95E1D3', '#F38181']

# Game 1: Clear FPS
game1_scores = np.array([4.5, -1.0, -0.5, -2.0, -1.5])
game1_probs = softmax(game1_scores)

# Game 2: Could be RPG or Strategy
game2_scores = np.array([-0.5, 2.5, 2.3, -1.0, 0.2])
game2_probs = softmax(game2_scores)

# Game 3: Racing game
game3_scores = np.array([0.3, -0.5, 0.1, 3.8, -1.0])
game3_probs = softmax(game3_scores)

# Game 4: Puzzle game
game4_scores = np.array([-1.5, 0.2, 0.5, -0.8, 3.2])
game4_probs = softmax(game4_scores)

games = [
    (game1_scores, game1_probs, 'Гра 1: "Fast shooter with guns"\nВпевнено FPS'),
    (game2_scores, game2_probs, 'Гра 2: "Build character, strategic combat"\nRPG чи Strategy?'),
    (game3_scores, game3_probs, 'Гра 3: "High speed cars on track"\nОчевидно Racing'),
    (game4_scores, game4_probs, 'Гра 4: "Match three colored blocks"\nPuzzle з високою впевненістю')
]

for ax, (scores, probs, title) in zip(axes.flat, games):
    x = np.arange(len(genres))
    width = 0.35

    # Plot scores and probabilities
    bars1 = ax.barh([i - width/2 for i in x], scores, width,
                    label='Скори', alpha=0.6, edgecolor='black')
    bars2 = ax.barh([i + width/2 for i in x], probs, width,
                    label='Ймовірності', alpha=0.8, edgecolor='black')

    # Color bars
    for i, (bar1, bar2) in enumerate(zip(bars1, bars2)):
        bar1.set_color(colors_5[i])
        bar2.set_color(colors_5[i])

    # Add value labels
    for i, (score, prob) in enumerate(zip(scores, probs)):
        if score > 0:
            ax.text(score + 0.2, i - width/2, f'{score:.1f}',
                   va='center', ha='left', fontsize=9, fontweight='bold')
        if prob > 0.05:
            ax.text(prob + 0.02, i + width/2, f'{prob:.2f}',
                   va='center', ha='left', fontsize=9, fontweight='bold')

    ax.set_yticks(x)
    ax.set_yticklabels(genres)
    ax.set_xlabel('Значення', fontsize=11)
    ax.set_title(title, fontsize=11, fontweight='bold')
    ax.legend(loc='lower right', fontsize=9)
    ax.grid(axis='x', alpha=0.3)

    # Highlight predicted class
    predicted_class = np.argmax(probs)
    ax.axhline(y=predicted_class, color='green', linestyle='--',
              linewidth=2, alpha=0.5)
    ax.text(0.98, 0.02, f'Передбачення: {genres[predicted_class]}',
           transform=ax.transAxes, fontsize=10,
           verticalalignment='bottom', horizontalalignment='right',
           bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))

plt.tight_layout(rect=[0, 0, 1, 0.97])
plt.savefig('softmax_game_genre_example.png', dpi=150, bbox_inches='tight')
print("✓ Saved: softmax_game_genre_example.png")
plt.close()

print("\n=== Softmax Visualization Complete ===")
print("\n5 visualizations created:")
print("1. softmax_basic_transformation.png - Basic concept with 3 examples")
print("2. softmax_temperature_effect.png - How temperature affects distribution")
print("3. softmax_vs_argmax.png - Comparison with hard classification")
print("4. softmax_computation_steps.png - Step-by-step computation")
print("5. softmax_game_genre_example.png - Real game genre classification examples")
print("\nAll images ready for review!")
