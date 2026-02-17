"""
Visualization of nonlinear decision boundaries in logistic regression
Shows how polynomial features enable circular/curved boundaries
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import PolynomialFeatures
from matplotlib.colors import ListedColormap

# Set random seed for reproducibility
np.random.seed(42)

# Generate synthetic data with circular boundary
n_samples = 200

# Class 0: points near the origin (inside circle)
theta_inner = np.random.uniform(0, 2*np.pi, n_samples//2)
r_inner = np.random.uniform(0, 1.5, n_samples//2)
X_inner = np.column_stack([r_inner * np.cos(theta_inner), r_inner * np.sin(theta_inner)])
y_inner = np.zeros(n_samples//2)

# Class 1: points farther from origin (outside circle)
theta_outer = np.random.uniform(0, 2*np.pi, n_samples//2)
r_outer = np.random.uniform(2.5, 4, n_samples//2)
X_outer = np.column_stack([r_outer * np.cos(theta_outer), r_outer * np.sin(theta_outer)])
y_outer = np.ones(n_samples//2)

# Combine datasets
X = np.vstack([X_inner, X_outer])
y = np.concatenate([y_inner, y_outer])

# Create mesh for visualization
h = 0.1  # step size
x_min, x_max = X[:, 0].min() - 0.5, X[:, 0].max() + 0.5
y_min, y_max = X[:, 1].min() - 0.5, X[:, 1].max() + 0.5
xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                     np.arange(y_min, y_max, h))

# Create figure with 3 subplots
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Define colors
cmap_light = ListedColormap(['#FFAAAA', '#AAAAFF'])
cmap_bold = ['#FF0000', '#0000FF']

# --- Subplot 1: Linear Logistic Regression (fails) ---
model_linear = LogisticRegression(max_iter=1000, random_state=42)
model_linear.fit(X, y)

# Predict on mesh
Z_linear = model_linear.predict(np.c_[xx.ravel(), yy.ravel()])
Z_linear = Z_linear.reshape(xx.shape)

axes[0].contourf(xx, yy, Z_linear, alpha=0.3, cmap=cmap_light)
axes[0].scatter(X[y == 0][:, 0], X[y == 0][:, 1], c=cmap_bold[0],
                edgecolor='k', s=50, label='Клас 0 (inner)')
axes[0].scatter(X[y == 1][:, 0], X[y == 1][:, 1], c=cmap_bold[1],
                edgecolor='k', s=50, label='Клас 1 (outer)')
axes[0].set_xlabel('x₁', fontsize=12)
axes[0].set_ylabel('x₂', fontsize=12)
axes[0].set_title('Лінійна логістична регресія\n(не справляється)', fontsize=13, weight='bold')
axes[0].legend(loc='upper right')
axes[0].set_xlim(xx.min(), xx.max())
axes[0].set_ylim(yy.min(), yy.max())
axes[0].grid(alpha=0.3)

# Add accuracy
acc_linear = model_linear.score(X, y)
axes[0].text(0.02, 0.98, f'Accuracy: {acc_linear:.2f}',
             transform=axes[0].transAxes, fontsize=11,
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# --- Subplot 2: Polynomial Features (degree=2) ---
poly2 = PolynomialFeatures(degree=2)
X_poly2 = poly2.fit_transform(X)

model_poly2 = LogisticRegression(max_iter=1000, random_state=42)
model_poly2.fit(X_poly2, y)

# Predict on mesh
X_mesh = np.c_[xx.ravel(), yy.ravel()]
X_mesh_poly2 = poly2.transform(X_mesh)
Z_poly2 = model_poly2.predict(X_mesh_poly2)
Z_poly2 = Z_poly2.reshape(xx.shape)

axes[1].contourf(xx, yy, Z_poly2, alpha=0.3, cmap=cmap_light)
axes[1].scatter(X[y == 0][:, 0], X[y == 0][:, 1], c=cmap_bold[0],
                edgecolor='k', s=50, label='Клас 0')
axes[1].scatter(X[y == 1][:, 0], X[y == 1][:, 1], c=cmap_bold[1],
                edgecolor='k', s=50, label='Клас 1')
axes[1].set_xlabel('x₁', fontsize=12)
axes[1].set_ylabel('x₂', fontsize=12)
axes[1].set_title('Поліноміальні ознаки (степінь 2)\n[x₁, x₂, x₁², x₂², x₁x₂]',
                  fontsize=13, weight='bold')
axes[1].legend(loc='upper right')
axes[1].set_xlim(xx.min(), xx.max())
axes[1].set_ylim(yy.min(), yy.max())
axes[1].grid(alpha=0.3)

# Add accuracy
acc_poly2 = model_poly2.score(X_poly2, y)
axes[1].text(0.02, 0.98, f'Accuracy: {acc_poly2:.2f}',
             transform=axes[1].transAxes, fontsize=11,
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))

# --- Subplot 3: Polynomial Features (degree=3) ---
poly3 = PolynomialFeatures(degree=3)
X_poly3 = poly3.fit_transform(X)

model_poly3 = LogisticRegression(max_iter=1000, random_state=42)
model_poly3.fit(X_poly3, y)

# Predict on mesh
X_mesh_poly3 = poly3.transform(X_mesh)
Z_poly3 = model_poly3.predict(X_mesh_poly3)
Z_poly3 = Z_poly3.reshape(xx.shape)

axes[2].contourf(xx, yy, Z_poly3, alpha=0.3, cmap=cmap_light)
axes[2].scatter(X[y == 0][:, 0], X[y == 0][:, 1], c=cmap_bold[0],
                edgecolor='k', s=50, label='Клас 0')
axes[2].scatter(X[y == 1][:, 0], X[y == 1][:, 1], c=cmap_bold[1],
                edgecolor='k', s=50, label='Клас 1')
axes[2].set_xlabel('x₁', fontsize=12)
axes[2].set_ylabel('x₂', fontsize=12)
axes[2].set_title('Поліноміальні ознаки (степінь 3)\n[x₁, x₂, ..., x₁³, x₂³, ...]',
                  fontsize=13, weight='bold')
axes[2].legend(loc='upper right')
axes[2].set_xlim(xx.min(), xx.max())
axes[2].set_ylim(yy.min(), yy.max())
axes[2].grid(alpha=0.3)

# Add accuracy
acc_poly3 = model_poly3.score(X_poly3, y)
axes[2].text(0.02, 0.98, f'Accuracy: {acc_poly3:.2f}',
             transform=axes[2].transAxes, fontsize=11,
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))

plt.tight_layout()
plt.savefig('nonlinear_logistic_regression.png', dpi=150, bbox_inches='tight')
print("✓ Saved: nonlinear_logistic_regression.png")
plt.close()

# Create a second visualization showing the transformation concept
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Left plot: Original 2D space with circular boundary
axes[0].scatter(X[y == 0][:, 0], X[y == 0][:, 1], c=cmap_bold[0],
                edgecolor='k', s=60, label='Клас 0 (inner)', alpha=0.7)
axes[0].scatter(X[y == 1][:, 0], X[y == 1][:, 1], c=cmap_bold[1],
                edgecolor='k', s=60, label='Клас 1 (outer)', alpha=0.7)

# Draw the ideal circular boundary
circle = plt.Circle((0, 0), 2, fill=False, color='green', linewidth=3,
                     linestyle='--', label='Ідеальна межа')
axes[0].add_patch(circle)

axes[0].set_xlabel('x₁', fontsize=13)
axes[0].set_ylabel('x₂', fontsize=13)
axes[0].set_title('Вихідний простір ознак\n(нелінійно розділювані)', fontsize=14, weight='bold')
axes[0].legend(loc='upper right', fontsize=11)
axes[0].set_xlim(-5, 5)
axes[0].set_ylim(-5, 5)
axes[0].grid(alpha=0.3)
axes[0].set_aspect('equal')

# Right plot: Show feature expansion concept (pseudo-3D view)
# Use distance from origin as the new feature
r = np.sqrt(X[:, 0]**2 + X[:, 1]**2)
axes[1].scatter(r[y == 0], X[y == 0][:, 1], c=cmap_bold[0],
                edgecolor='k', s=60, label='Клас 0', alpha=0.7)
axes[1].scatter(r[y == 1], X[y == 1][:, 1], c=cmap_bold[1],
                edgecolor='k', s=60, label='Клас 1', alpha=0.7)

# Draw a vertical line showing linear separability in transformed space
axes[1].axvline(x=2, color='green', linewidth=3, linestyle='--',
                label='Лінійна межа у новому просторі')

axes[1].set_xlabel('r = √(x₁² + x₂²)  [нова ознака]', fontsize=13)
axes[1].set_ylabel('x₂', fontsize=13)
axes[1].set_title('Розширений простір ознак\n(лінійно розділювані!)', fontsize=14, weight='bold')
axes[1].legend(loc='upper right', fontsize=11)
axes[1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig('feature_space_transformation.png', dpi=150, bbox_inches='tight')
print("✓ Saved: feature_space_transformation.png")
plt.close()

print("\nДві візуалізації успішно створено:")
print("1. nonlinear_logistic_regression.png - порівняння лінійної vs поліноміальної логістичної регресії")
print("2. feature_space_transformation.png - ілюстрація трансформації простору ознак")
