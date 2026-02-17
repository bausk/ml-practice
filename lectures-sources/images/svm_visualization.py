"""
Visualization of SVM concepts for lecture 3
Shows: Logistic Regression vs SVM boundary comparison, margin, support vectors,
and kernel trick for nonlinear data
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from matplotlib.colors import ListedColormap
from matplotlib.patches import FancyArrowPatch

# Set random seed for reproducibility
np.random.seed(42)

# ============================================================
# Figure 1: Logistic Regression vs SVM — margin concept
# ============================================================

# Generate linearly separable data with some gap
n = 40
X_class0 = np.random.randn(n, 2) * 0.7 + np.array([-1.5, -1.0])
X_class1 = np.random.randn(n, 2) * 0.7 + np.array([1.5, 1.0])
X = np.vstack([X_class0, X_class1])
y = np.array([0] * n + [1] * n)

fig, axes = plt.subplots(1, 3, figsize=(19, 5.5))

cmap_light = ListedColormap(['#FFCCCC', '#CCCCFF'])
colors = ['#CC0000', '#0000CC']

# --- Panel 1: Logistic Regression ---
lr = LogisticRegression(C=100, random_state=42)
lr.fit(X, y)

h = 0.05
x_min, x_max = X[:, 0].min() - 1.5, X[:, 0].max() + 1.5
y_min, y_max = X[:, 1].min() - 1.5, X[:, 1].max() + 1.5
xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))

Z_lr = lr.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
axes[0].contourf(xx, yy, Z_lr, alpha=0.2, cmap=cmap_light)

# Draw decision boundary
w = lr.coef_[0]
b = lr.intercept_[0]
x_line = np.linspace(x_min, x_max, 100)
y_line = -(w[0] * x_line + b) / w[1]
axes[0].plot(x_line, y_line, 'k-', linewidth=2.5, label='Межа рішень')

axes[0].scatter(X[y == 0][:, 0], X[y == 0][:, 1], c=colors[0],
                edgecolor='k', s=60, label='Клас 0', zorder=3)
axes[0].scatter(X[y == 1][:, 0], X[y == 1][:, 1], c=colors[1],
                edgecolor='k', s=60, label='Клас 1', zorder=3)

axes[0].set_xlabel('x₁', fontsize=13)
axes[0].set_ylabel('x₂', fontsize=13)
axes[0].set_title('Логістична регресія\n(максимум ймовірності)', fontsize=14, weight='bold')
axes[0].legend(loc='upper left', fontsize=10)
axes[0].set_xlim(x_min, x_max)
axes[0].set_ylim(y_min, y_max)
axes[0].grid(alpha=0.2)

# --- Panel 2: SVM with margin ---
svm = SVC(kernel='linear', C=100, random_state=42)
svm.fit(X, y)

Z_svm = svm.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
axes[1].contourf(xx, yy, Z_svm, alpha=0.2, cmap=cmap_light)

# Decision boundary and margins
w_svm = svm.coef_[0]
b_svm = svm.intercept_[0]
margin = 1 / np.linalg.norm(w_svm)

y_boundary = -(w_svm[0] * x_line + b_svm) / w_svm[1]
y_margin_pos = -(w_svm[0] * x_line + b_svm - 1) / w_svm[1]
y_margin_neg = -(w_svm[0] * x_line + b_svm + 1) / w_svm[1]

axes[1].plot(x_line, y_boundary, 'k-', linewidth=2.5, label='Межа рішень')
axes[1].plot(x_line, y_margin_pos, 'k--', linewidth=1.5, alpha=0.6)
axes[1].plot(x_line, y_margin_neg, 'k--', linewidth=1.5, alpha=0.6)

# Fill margin area
axes[1].fill_between(x_line, y_margin_neg, y_margin_pos, alpha=0.08,
                      color='green', label='Відступ (margin)')

# Plot all points
axes[1].scatter(X[y == 0][:, 0], X[y == 0][:, 1], c=colors[0],
                edgecolor='k', s=60, zorder=3)
axes[1].scatter(X[y == 1][:, 0], X[y == 1][:, 1], c=colors[1],
                edgecolor='k', s=60, zorder=3)

# Highlight support vectors
sv = svm.support_vectors_
axes[1].scatter(sv[:, 0], sv[:, 1], s=200, facecolors='none',
                edgecolors='#00AA00', linewidths=3, zorder=4,
                label=f'Опорні вектори ({len(sv)} шт.)')

# Draw arrow showing margin width
mid_idx = len(x_line) // 2
mid_x = x_line[mid_idx]
mid_y_neg = y_margin_neg[mid_idx]
mid_y_pos = y_margin_pos[mid_idx]
mid_y_center = y_boundary[mid_idx]

# Perpendicular direction to the boundary
w_norm = w_svm / np.linalg.norm(w_svm)
arrow_start = np.array([mid_x, mid_y_center]) - w_norm * margin
arrow_end = np.array([mid_x, mid_y_center]) + w_norm * margin
axes[1].annotate('', xy=arrow_end, xytext=arrow_start,
                 arrowprops=dict(arrowstyle='<->', color='green', lw=2.5))
# Label the margin
label_pos = np.array([mid_x, mid_y_center]) + np.array([0.3, -0.3])
axes[1].text(label_pos[0], label_pos[1], 'margin',
             fontsize=12, color='green', weight='bold',
             bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))

axes[1].set_xlabel('x₁', fontsize=13)
axes[1].set_ylabel('x₂', fontsize=13)
axes[1].set_title('SVM (лінійне ядро)\n(максимальний відступ)', fontsize=14, weight='bold')
axes[1].legend(loc='upper left', fontsize=10)
axes[1].set_xlim(x_min, x_max)
axes[1].set_ylim(y_min, y_max)
axes[1].grid(alpha=0.2)

# --- Panel 3: Kernel trick — RBF for nonlinear data ---
# Generate nonlinear data (XOR-like pattern)
np.random.seed(42)
n_nl = 80
# Four clusters in XOR arrangement
X_nl_00 = np.random.randn(n_nl // 4, 2) * 0.5 + np.array([-1.5, -1.5])
X_nl_01 = np.random.randn(n_nl // 4, 2) * 0.5 + np.array([-1.5, 1.5])
X_nl_10 = np.random.randn(n_nl // 4, 2) * 0.5 + np.array([1.5, -1.5])
X_nl_11 = np.random.randn(n_nl // 4, 2) * 0.5 + np.array([1.5, 1.5])

X_nl = np.vstack([X_nl_00, X_nl_11, X_nl_01, X_nl_10])
y_nl = np.array([0] * (n_nl // 4) + [0] * (n_nl // 4) +
                 [1] * (n_nl // 4) + [1] * (n_nl // 4))

svm_rbf = SVC(kernel='rbf', C=10, gamma=0.5, random_state=42)
svm_rbf.fit(X_nl, y_nl)

x_min_nl, x_max_nl = X_nl[:, 0].min() - 1.0, X_nl[:, 0].max() + 1.0
y_min_nl, y_max_nl = X_nl[:, 1].min() - 1.0, X_nl[:, 1].max() + 1.0
xx_nl, yy_nl = np.meshgrid(np.arange(x_min_nl, x_max_nl, h),
                             np.arange(y_min_nl, y_max_nl, h))

Z_rbf = svm_rbf.predict(np.c_[xx_nl.ravel(), yy_nl.ravel()]).reshape(xx_nl.shape)
axes[2].contourf(xx_nl, yy_nl, Z_rbf, alpha=0.2, cmap=cmap_light)

# Draw decision boundary contour
Z_decision = svm_rbf.decision_function(np.c_[xx_nl.ravel(), yy_nl.ravel()]).reshape(xx_nl.shape)
axes[2].contour(xx_nl, yy_nl, Z_decision, levels=[0], colors='k', linewidths=2.5)
axes[2].contour(xx_nl, yy_nl, Z_decision, levels=[-1, 1], colors='k',
                linewidths=1.5, linestyles='dashed', alpha=0.5)

axes[2].scatter(X_nl[y_nl == 0][:, 0], X_nl[y_nl == 0][:, 1], c=colors[0],
                edgecolor='k', s=60, label='Клас 0', zorder=3)
axes[2].scatter(X_nl[y_nl == 1][:, 0], X_nl[y_nl == 1][:, 1], c=colors[1],
                edgecolor='k', s=60, label='Клас 1', zorder=3)

# Highlight support vectors
sv_rbf = svm_rbf.support_vectors_
axes[2].scatter(sv_rbf[:, 0], sv_rbf[:, 1], s=200, facecolors='none',
                edgecolors='#00AA00', linewidths=2.5, zorder=4,
                label=f'Опорні вектори ({len(sv_rbf)} шт.)')

axes[2].set_xlabel('x₁', fontsize=13)
axes[2].set_ylabel('x₂', fontsize=13)
axes[2].set_title('SVM (RBF-ядро)\n(нелінійна межа — XOR-задача)', fontsize=14, weight='bold')
axes[2].legend(loc='upper left', fontsize=10)
axes[2].set_xlim(x_min_nl, x_max_nl)
axes[2].set_ylim(y_min_nl, y_max_nl)
axes[2].grid(alpha=0.2)

plt.tight_layout()
plt.savefig('svm_comparison.png', dpi=150, bbox_inches='tight')
print("✓ Saved: svm_comparison.png")
plt.close()

# ============================================================
# Figure 2: The "road between villages" analogy
# ============================================================

fig, axes = plt.subplots(1, 2, figsize=(15, 6))

# Generate well-separated data for clear illustration
np.random.seed(123)
n_demo = 25
X_a = np.random.randn(n_demo, 2) * 0.6 + np.array([-2.0, 0])
X_b = np.random.randn(n_demo, 2) * 0.6 + np.array([2.0, 0])
X_demo = np.vstack([X_a, X_b])
y_demo = np.array([0] * n_demo + [1] * n_demo)

# --- Panel 1: Logistic Regression — multiple possible boundaries ---
lr_demo = LogisticRegression(C=100, random_state=42)
lr_demo.fit(X_demo, y_demo)

axes[0].scatter(X_a[:, 0], X_a[:, 1], c=colors[0], edgecolor='k', s=80,
                label='Село A', zorder=3, marker='s')
axes[0].scatter(X_b[:, 0], X_b[:, 1], c=colors[1], edgecolor='k', s=80,
                label='Село B', zorder=3, marker='s')

# Draw the LR boundary
w_lr = lr_demo.coef_[0]
b_lr = lr_demo.intercept_[0]
x_plot = np.linspace(-4, 4, 100)
y_lr_line = -(w_lr[0] * x_plot + b_lr) / w_lr[1]
axes[0].plot(x_plot, y_lr_line, 'k-', linewidth=2.5, label='Межа (логіст. регресія)')

# Show a few alternative boundaries that also separate correctly
for angle_offset, style in [(-0.3, ':'), (0.2, '-.')]:
    w_alt = w_lr.copy()
    w_alt[1] += angle_offset
    y_alt = -(w_alt[0] * x_plot + b_lr) / w_alt[1]
    axes[0].plot(x_plot, y_alt, style, color='gray', linewidth=1.5, alpha=0.6)

axes[0].text(0, 2.5, 'Багато можливих\nмеж розділяють\nкласи правильно',
             ha='center', fontsize=12, color='gray', style='italic',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.8))

axes[0].set_xlabel('x₁', fontsize=13)
axes[0].set_ylabel('x₂', fontsize=13)
axes[0].set_title('Логістична регресія\n«Будь-яка дорога, що розділяє села»', fontsize=14, weight='bold')
axes[0].legend(loc='lower left', fontsize=10)
axes[0].set_xlim(-4.5, 4.5)
axes[0].set_ylim(-3.5, 3.5)
axes[0].grid(alpha=0.2)

# --- Panel 2: SVM — unique optimal boundary with maximum margin ---
svm_demo = SVC(kernel='linear', C=100, random_state=42)
svm_demo.fit(X_demo, y_demo)

axes[1].scatter(X_a[:, 0], X_a[:, 1], c=colors[0], edgecolor='k', s=80,
                label='Село A', zorder=3, marker='s')
axes[1].scatter(X_b[:, 0], X_b[:, 1], c=colors[1], edgecolor='k', s=80,
                label='Село B', zorder=3, marker='s')

w_s = svm_demo.coef_[0]
b_s = svm_demo.intercept_[0]
margin_s = 1 / np.linalg.norm(w_s)

y_s_line = -(w_s[0] * x_plot + b_s) / w_s[1]
y_s_pos = -(w_s[0] * x_plot + b_s - 1) / w_s[1]
y_s_neg = -(w_s[0] * x_plot + b_s + 1) / w_s[1]

axes[1].plot(x_plot, y_s_line, 'k-', linewidth=2.5, label='Оптимальна межа (SVM)')
axes[1].plot(x_plot, y_s_pos, 'k--', linewidth=1.5, alpha=0.5)
axes[1].plot(x_plot, y_s_neg, 'k--', linewidth=1.5, alpha=0.5)
axes[1].fill_between(x_plot, y_s_neg, y_s_pos, alpha=0.12,
                      color='green', label='Максимальний відступ')

# Support vectors
sv_demo = svm_demo.support_vectors_
axes[1].scatter(sv_demo[:, 0], sv_demo[:, 1], s=250, facecolors='none',
                edgecolors='#00AA00', linewidths=3, zorder=4,
                label=f'Опорні вектори ({len(sv_demo)} шт.)')

# Annotate margin
w_s_norm = w_s / np.linalg.norm(w_s)
center_y = -(w_s[0] * 0 + b_s) / w_s[1]
arr_start = np.array([0, center_y]) - w_s_norm * margin_s
arr_end = np.array([0, center_y]) + w_s_norm * margin_s
axes[1].annotate('', xy=arr_end, xytext=arr_start,
                 arrowprops=dict(arrowstyle='<->', color='green', lw=2.5))
axes[1].text(0.3, center_y - 0.4, 'макс. відступ',
             fontsize=12, color='green', weight='bold',
             bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))

axes[1].text(0, 2.5, 'Єдина оптимальна\nмежа — якомога далі\nвід крайніх будинків',
             ha='center', fontsize=12, color='#006600', style='italic',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='#e6ffe6', alpha=0.8))

axes[1].set_xlabel('x₁', fontsize=13)
axes[1].set_ylabel('x₂', fontsize=13)
axes[1].set_title('SVM\n«Дорога якомога далі від обох сіл»', fontsize=14, weight='bold')
axes[1].legend(loc='lower left', fontsize=10)
axes[1].set_xlim(-4.5, 4.5)
axes[1].set_ylim(-3.5, 3.5)
axes[1].grid(alpha=0.2)

plt.tight_layout()
plt.savefig('svm_margin_analogy.png', dpi=150, bbox_inches='tight')
print("✓ Saved: svm_margin_analogy.png")
plt.close()

print("\nДві SVM-візуалізації успішно створено:")
print("1. svm_comparison.png — логістична регресія vs SVM (лінійне ядро) vs SVM (RBF-ядро)")
print("2. svm_margin_analogy.png — аналогія «дорога між селами» (лог. регресія vs SVM)")
