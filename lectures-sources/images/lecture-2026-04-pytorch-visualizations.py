"""
Visualizations for Lecture 4: PyTorch Fundamentals
Generates visual aids for tensor distributions, activation functions,
autograd computational graph, network architecture, training loop, and learning curve.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import seaborn as sns

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Use a font that supports Ukrainian characters
plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial', 'Helvetica', 'sans-serif']

# ============================================================================
# Figure 1: Tensor Distributions (rand vs randn)
# ============================================================================
print("Generating Figure 1: Tensor distributions...")

np.random.seed(42)
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# torch.rand() equivalent
uniform_data = np.random.uniform(0, 1, 10000)
axes[0].hist(uniform_data, bins=50, color='#4ECDC4', alpha=0.8, edgecolor='black', linewidth=0.5)
axes[0].set_title('torch.rand(10000)\nUniform [0, 1)', fontsize=14, fontweight='bold')
axes[0].set_xlabel('Value', fontsize=12)
axes[0].set_ylabel('Count', fontsize=12)
axes[0].axvline(x=0.5, color='red', linestyle='--', linewidth=2, label='mean = 0.5')
axes[0].legend(fontsize=11)
axes[0].set_xlim(-0.1, 1.1)

# torch.randn() equivalent
normal_data = np.random.randn(10000)
axes[1].hist(normal_data, bins=50, color='#FF6B6B', alpha=0.8, edgecolor='black', linewidth=0.5)
axes[1].set_title('torch.randn(10000)\nNormal (mean=0, std=1)', fontsize=14, fontweight='bold')
axes[1].set_xlabel('Value', fontsize=12)
axes[1].set_ylabel('Count', fontsize=12)
axes[1].axvline(x=0, color='blue', linestyle='--', linewidth=2, label='mean = 0')
axes[1].legend(fontsize=11)

plt.tight_layout()
plt.savefig('lecture-2026-04-pytorch-tensor-distributions.png', dpi=150, bbox_inches='tight')
print("  Saved: lecture-2026-04-pytorch-tensor-distributions.png")
plt.close()

# ============================================================================
# Figure 2: Activation Functions (ReLU, Sigmoid, Tanh)
# ============================================================================
print("Generating Figure 2: Activation functions...")

fig, axes = plt.subplots(1, 3, figsize=(16, 5))

x = np.linspace(-5, 5, 200)

# ReLU
relu = np.maximum(0, x)
axes[0].plot(x, relu, color='#FF6B6B', linewidth=3, label='ReLU(z) = max(0, z)')
axes[0].fill_between(x, relu, alpha=0.15, color='#FF6B6B')
axes[0].axhline(y=0, color='gray', linestyle='-', linewidth=0.5)
axes[0].axvline(x=0, color='gray', linestyle='-', linewidth=0.5)
axes[0].set_title('ReLU', fontsize=16, fontweight='bold')
axes[0].set_xlabel('z', fontsize=13)
axes[0].set_ylabel('f(z)', fontsize=13)
axes[0].legend(fontsize=11, loc='upper left')
axes[0].set_ylim(-1, 5.5)
axes[0].text(2.5, 4.5, 'gradient = 1', fontsize=11, color='#FF6B6B',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
axes[0].text(-4.5, 0.5, 'gradient = 0', fontsize=11, color='gray',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

# Sigmoid
sigmoid = 1 / (1 + np.exp(-x))
axes[1].plot(x, sigmoid, color='#4ECDC4', linewidth=3, label=r'$\sigma(z) = \frac{1}{1+e^{-z}}$')
axes[1].fill_between(x, sigmoid, alpha=0.15, color='#4ECDC4')
axes[1].axhline(y=0.5, color='orange', linestyle='--', linewidth=1.5, alpha=0.7, label='y = 0.5')
axes[1].axhline(y=0, color='gray', linestyle='-', linewidth=0.5)
axes[1].axhline(y=1, color='gray', linestyle='--', linewidth=0.5, alpha=0.5)
axes[1].axvline(x=0, color='gray', linestyle='-', linewidth=0.5)
axes[1].set_title('Sigmoid', fontsize=16, fontweight='bold')
axes[1].set_xlabel('z', fontsize=13)
axes[1].set_ylabel('f(z)', fontsize=13)
axes[1].legend(fontsize=11, loc='upper left')
axes[1].set_ylim(-0.1, 1.15)
axes[1].text(1.5, 0.15, 'output: (0, 1)', fontsize=11, color='#4ECDC4',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

# Tanh
tanh = np.tanh(x)
axes[2].plot(x, tanh, color='#45B7D1', linewidth=3, label=r'tanh(z) = $\frac{e^z - e^{-z}}{e^z + e^{-z}}$')
axes[2].fill_between(x, tanh, alpha=0.15, color='#45B7D1')
axes[2].axhline(y=0, color='gray', linestyle='-', linewidth=0.5)
axes[2].axhline(y=1, color='gray', linestyle='--', linewidth=0.5, alpha=0.5)
axes[2].axhline(y=-1, color='gray', linestyle='--', linewidth=0.5, alpha=0.5)
axes[2].axvline(x=0, color='gray', linestyle='-', linewidth=0.5)
axes[2].set_title('Tanh', fontsize=16, fontweight='bold')
axes[2].set_xlabel('z', fontsize=13)
axes[2].set_ylabel('f(z)', fontsize=13)
axes[2].legend(fontsize=11, loc='upper left')
axes[2].set_ylim(-1.3, 1.3)
axes[2].text(1.5, -0.7, 'output: (-1, 1)', fontsize=11, color='#45B7D1',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

plt.tight_layout()
plt.savefig('lecture-2026-04-pytorch-activations.png', dpi=150, bbox_inches='tight')
print("  Saved: lecture-2026-04-pytorch-activations.png")
plt.close()

# ============================================================================
# Figure 3: Autograd Computational Graph
# ============================================================================
print("Generating Figure 3: Autograd computational graph...")

fig, ax = plt.subplots(1, 1, figsize=(14, 8))
ax.set_xlim(0, 14)
ax.set_ylim(0, 10)
ax.axis('off')

# Node style
def draw_node(ax, x, y, text, color='#E8F4FD', width=1.6, height=0.7, fontsize=12):
    bbox = FancyBboxPatch((x - width/2, y - height/2), width, height,
                          boxstyle="round,pad=0.1", facecolor=color,
                          edgecolor='black', linewidth=2)
    ax.add_patch(bbox)
    ax.text(x, y, text, ha='center', va='center', fontsize=fontsize, fontweight='bold')

def draw_arrow(ax, x1, y1, x2, y2, color='black', style='->', lw=2):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color, lw=lw))

# Input variables
draw_node(ax, 1.5, 8.5, 'x = 1.0', color='#FFE0B2', width=1.8)
draw_node(ax, 5.0, 8.5, 'y = 2.0', color='#FFE0B2', width=1.8)
draw_node(ax, 9.0, 8.5, 'z = 0.5', color='#FFE0B2', width=1.8)

# Operations - level 1
draw_node(ax, 1.5, 6.5, 'sin(x)', color='#C8E6C9', width=1.8)
draw_node(ax, 5.0, 6.5, 'y\u00b2', color='#C8E6C9', width=1.4)
draw_node(ax, 9.0, 6.5, 'exp(z)', color='#C8E6C9', width=1.8)

# Operations - level 2
draw_node(ax, 3.25, 4.5, 'sin(x) \u00b7 y\u00b2', color='#BBDEFB', width=2.4)
draw_node(ax, 9.0, 4.5, 'exp(z)', color='#BBDEFB', width=1.8)

# Final output
draw_node(ax, 6.0, 2.5, 'f = sin(x)\u00b7y\u00b2 + exp(z)', color='#F8BBD0', width=4.0, height=0.8, fontsize=13)

# Forward arrows (solid)
draw_arrow(ax, 1.5, 8.1, 1.5, 6.9)
draw_arrow(ax, 5.0, 8.1, 5.0, 6.9)
draw_arrow(ax, 9.0, 8.1, 9.0, 6.9)

draw_arrow(ax, 1.5, 6.1, 3.25, 4.9)
draw_arrow(ax, 5.0, 6.1, 3.25, 4.9)
draw_arrow(ax, 9.0, 6.1, 9.0, 4.9)

draw_arrow(ax, 3.25, 4.1, 6.0, 2.9)
draw_arrow(ax, 9.0, 4.1, 6.0, 2.9)

# Gradient annotations (on the right side)
ax.text(11.5, 8.5, 'requires_grad=True', fontsize=10, color='#E65100',
        ha='left', va='center', style='italic',
        bbox=dict(boxstyle='round', facecolor='#FFF3E0', alpha=0.8))

ax.text(11.5, 2.5, '.backward()', fontsize=12, color='#C62828',
        ha='left', va='center', fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='#FFEBEE', alpha=0.8))

# Backward arrows (dashed red)
draw_arrow(ax, 5.5, 2.9, 3.25, 4.1, color='red', style='->', lw=1.5)
draw_arrow(ax, 6.5, 2.9, 9.0, 4.1, color='red', style='->', lw=1.5)
draw_arrow(ax, 2.5, 4.5, 1.5, 6.1, color='red', style='->', lw=1.5)
draw_arrow(ax, 4.0, 4.5, 5.0, 6.1, color='red', style='->', lw=1.5)

# Gradient values
ax.text(0.0, 6.5, 'x.grad\n\u2248 2.16', fontsize=10, color='red',
        ha='center', va='center',
        bbox=dict(boxstyle='round', facecolor='#FFCDD2', alpha=0.7))
ax.text(6.5, 6.5, 'y.grad\n\u2248 3.37', fontsize=10, color='red',
        ha='center', va='center',
        bbox=dict(boxstyle='round', facecolor='#FFCDD2', alpha=0.7))
ax.text(10.8, 6.0, 'z.grad\n\u2248 1.65', fontsize=10, color='red',
        ha='center', va='center',
        bbox=dict(boxstyle='round', facecolor='#FFCDD2', alpha=0.7))

# Title
ax.set_title('Autograd: Computational Graph\nf(x, y, z) = sin(x) \u00b7 y\u00b2 + exp(z)',
             fontsize=16, fontweight='bold', pad=15)

# Legend
forward_patch = mpatches.Patch(color='black', label='Forward pass')
backward_patch = mpatches.Patch(color='red', label='Backward pass (gradients)')
ax.legend(handles=[forward_patch, backward_patch], loc='lower left', fontsize=12,
          framealpha=0.9)

plt.tight_layout()
plt.savefig('lecture-2026-04-pytorch-autograd.png', dpi=150, bbox_inches='tight')
print("  Saved: lecture-2026-04-pytorch-autograd.png")
plt.close()

# ============================================================================
# Figure 4: Neural Network Architecture
# ============================================================================
print("Generating Figure 4: Network architecture...")

fig, ax = plt.subplots(1, 1, figsize=(14, 7))
ax.set_xlim(-1, 15)
ax.set_ylim(-1, 9)
ax.axis('off')

# Layer positions
layers = [
    {'x': 1.5, 'n': 6, 'label': 'Input\n87 features', 'color': '#FFE0B2', 'sublabel': '...'},
    {'x': 5.0, 'n': 5, 'label': 'Hidden 1\n64 neurons', 'color': '#C8E6C9', 'sublabel': 'ReLU'},
    {'x': 8.5, 'n': 4, 'label': 'Hidden 2\n32 neurons', 'color': '#BBDEFB', 'sublabel': 'ReLU'},
    {'x': 12.0, 'n': 1, 'label': 'Output\n1 neuron', 'color': '#F8BBD0', 'sublabel': 'Price'},
]

def draw_layer(ax, x, n, label, color, sublabel, y_center=4.0, spacing=1.0):
    """Draw neurons for a layer."""
    positions = []
    total_height = (n - 1) * spacing
    y_start = y_center + total_height / 2

    for i in range(n):
        y = y_start - i * spacing
        circle = plt.Circle((x, y), 0.3, color=color, ec='black', linewidth=2, zorder=5)
        ax.add_patch(circle)
        positions.append((x, y))

    # Layer label
    ax.text(x, y_center - total_height / 2 - 1.0, label, ha='center', va='top',
            fontsize=11, fontweight='bold')
    if sublabel and sublabel != '...':
        ax.text(x, y_center + total_height / 2 + 0.7, sublabel, ha='center', va='bottom',
                fontsize=10, color='#666', style='italic',
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))

    return positions

# Draw layers
all_positions = []
for layer in layers:
    positions = draw_layer(ax, layer['x'], layer['n'], layer['label'],
                          layer['color'], layer['sublabel'])
    all_positions.append(positions)

# Draw connections between adjacent layers
for i in range(len(all_positions) - 1):
    for p1 in all_positions[i]:
        for p2 in all_positions[i + 1]:
            ax.plot([p1[0] + 0.3, p2[0] - 0.3], [p1[1], p2[1]],
                   color='gray', linewidth=0.5, alpha=0.3, zorder=1)

# Add "..." for input layer
ax.text(1.5, 4.0, '...', ha='center', va='center', fontsize=16, fontweight='bold',
        color='gray', zorder=10)

# Add parameter counts between layers
ax.text(3.25, 8.0, '87\u00d764 + 64\n= 5,632', ha='center', va='center',
        fontsize=9, color='#555',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
ax.text(6.75, 8.0, '64\u00d732 + 32\n= 2,080', ha='center', va='center',
        fontsize=9, color='#555',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
ax.text(10.25, 8.0, '32\u00d71 + 1\n= 33', ha='center', va='center',
        fontsize=9, color='#555',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

# Total
ax.text(7.0, -0.5, 'Total: 5,632 + 2,080 + 33 = 7,745 parameters',
        ha='center', va='center', fontsize=12, fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9))

# Arrow showing data flow
ax.annotate('', xy=(13.5, 4.0), xytext=(-0.5, 4.0),
            arrowprops=dict(arrowstyle='->', color='#2196F3', lw=2.5, ls='--'))

ax.set_title('HousePriceNet Architecture', fontsize=16, fontweight='bold', pad=15)

plt.tight_layout()
plt.savefig('lecture-2026-04-pytorch-architecture.png', dpi=150, bbox_inches='tight')
print("  Saved: lecture-2026-04-pytorch-architecture.png")
plt.close()

# ============================================================================
# Figure 5: Training Loop Diagram
# ============================================================================
print("Generating Figure 5: Training loop...")

fig, ax = plt.subplots(1, 1, figsize=(14, 6))
ax.set_xlim(0, 16)
ax.set_ylim(0, 7)
ax.axis('off')

# Step boxes
steps = [
    {'x': 2, 'y': 3.5, 'title': '1. Forward Pass', 'code': 'pred = model(X)',
     'desc': 'predictions', 'color': '#C8E6C9'},
    {'x': 5.5, 'y': 3.5, 'title': '2. Loss', 'code': 'loss = criterion(pred, y)',
     'desc': 'error', 'color': '#BBDEFB'},
    {'x': 9.5, 'y': 3.5, 'title': '3. Backward', 'code': 'loss.backward()',
     'desc': 'gradients', 'color': '#F8BBD0'},
    {'x': 13.5, 'y': 3.5, 'title': '4. Update', 'code': 'optimizer.step()',
     'desc': 'new weights', 'color': '#FFE0B2'},
]

for step in steps:
    # Main box
    bbox = FancyBboxPatch((step['x'] - 1.4, step['y'] - 1.2), 2.8, 2.4,
                          boxstyle="round,pad=0.15", facecolor=step['color'],
                          edgecolor='black', linewidth=2)
    ax.add_patch(bbox)

    # Title
    ax.text(step['x'], step['y'] + 0.6, step['title'],
            ha='center', va='center', fontsize=12, fontweight='bold')

    # Code
    ax.text(step['x'], step['y'] - 0.1, step['code'],
            ha='center', va='center', fontsize=9, fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    # Description
    ax.text(step['x'], step['y'] - 0.7, step['desc'],
            ha='center', va='center', fontsize=10, color='#555', style='italic')

# Arrows between steps
for i in range(len(steps) - 1):
    ax.annotate('', xy=(steps[i+1]['x'] - 1.5, steps[i+1]['y']),
                xytext=(steps[i]['x'] + 1.5, steps[i]['y']),
                arrowprops=dict(arrowstyle='->', color='#333', lw=2.5))

# Loop arrow (from step 4 back to step 1)
from matplotlib.patches import Arc
loop_arc = Arc((7.75, 0.5), 13, 2.5, angle=0, theta1=5, theta2=175,
               color='#2196F3', linewidth=2.5, linestyle='--')
ax.add_patch(loop_arc)
ax.annotate('', xy=(1.3, 1.2), xytext=(1.6, 0.9),
            arrowprops=dict(arrowstyle='->', color='#2196F3', lw=2.5))
ax.text(7.75, 0.3, 'repeat for each epoch', ha='center', va='center',
        fontsize=11, color='#2196F3', fontweight='bold', style='italic')

# zero_grad annotation
ax.text(8.0, 6.2, 'optimizer.zero_grad()', ha='center', va='center',
        fontsize=10, fontfamily='monospace', color='red',
        bbox=dict(boxstyle='round', facecolor='#FFCDD2', alpha=0.8))
ax.annotate('', xy=(9.5, 5.0), xytext=(8.5, 5.9),
            arrowprops=dict(arrowstyle='->', color='red', lw=1.5, ls='--'))

ax.set_title('PyTorch Training Loop', fontsize=16, fontweight='bold', pad=15)

plt.tight_layout()
plt.savefig('lecture-2026-04-pytorch-training-loop.png', dpi=150, bbox_inches='tight')
print("  Saved: lecture-2026-04-pytorch-training-loop.png")
plt.close()

# ============================================================================
# Figure 6: Learning Curve
# ============================================================================
print("Generating Figure 6: Learning curve...")

fig, ax = plt.subplots(1, 1, figsize=(10, 6))

np.random.seed(42)
epochs = np.arange(1, 101)

# Simulated training loss (exponential decay with noise)
train_loss = 5.0 * np.exp(-0.05 * epochs) + 0.3 + np.random.randn(100) * 0.08
train_loss = np.maximum(train_loss, 0.25)

# Simulated validation loss (slightly higher, starts increasing at the end)
val_loss = 5.0 * np.exp(-0.04 * epochs) + 0.5 + np.random.randn(100) * 0.1
val_loss = np.maximum(val_loss, 0.4)
# Add slight overfitting after epoch 70
val_loss[70:] += np.linspace(0, 0.4, 30) + np.random.randn(30) * 0.05

ax.plot(epochs, train_loss, color='#2196F3', linewidth=2.5, label='Training Loss', alpha=0.9)
ax.plot(epochs, val_loss, color='#FF6B6B', linewidth=2.5, label='Validation Loss', alpha=0.9)

# Mark overfitting region
ax.axvspan(70, 100, alpha=0.1, color='red')
ax.text(85, 3.5, 'Overfitting\nzone', ha='center', va='center',
        fontsize=12, color='red', fontweight='bold', style='italic',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

# Mark best model
best_epoch = 68
ax.axvline(x=best_epoch, color='green', linestyle='--', linewidth=1.5, alpha=0.7)
ax.text(best_epoch - 2, 4.5, f'Best model\nepoch {best_epoch}', ha='right', va='center',
        fontsize=11, color='green', fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='#C8E6C9', alpha=0.7))

ax.set_xlabel('Epoch', fontsize=13)
ax.set_ylabel('Loss (MSE)', fontsize=13)
ax.set_title('Learning Curve: Training vs Validation Loss', fontsize=15, fontweight='bold')
ax.legend(fontsize=12, loc='upper right')
ax.grid(True, alpha=0.3)
ax.set_xlim(1, 100)
ax.set_ylim(0, 5.5)

plt.tight_layout()
plt.savefig('lecture-2026-04-pytorch-learning-curve.png', dpi=150, bbox_inches='tight')
print("  Saved: lecture-2026-04-pytorch-learning-curve.png")
plt.close()

print("\n=== PyTorch Fundamentals Visualization Complete ===")
print("\n6 visualizations created:")
print("1. lecture-2026-04-pytorch-tensor-distributions.png - rand vs randn")
print("2. lecture-2026-04-pytorch-activations.png - ReLU, Sigmoid, Tanh")
print("3. lecture-2026-04-pytorch-autograd.png - Computational graph")
print("4. lecture-2026-04-pytorch-architecture.png - Network architecture")
print("5. lecture-2026-04-pytorch-training-loop.png - Training loop diagram")
print("6. lecture-2026-04-pytorch-learning-curve.png - Learning curve")
print("\nAll images ready for the lecture!")
