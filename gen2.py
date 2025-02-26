import matplotlib.pyplot as plt
import numpy as np
from sklearn.datasets import make_blobs

# Generate sample data
X, y = make_blobs(n_samples=300, centers=3, cluster_std=0.60, random_state=0)

# Plot the data
plt.figure(figsize=(8, 6))
plt.scatter(X[:, 0], X[:, 1], c=y, s=50, cmap='viridis')

# Mark the centroids
centers = np.array([[1, 4], [-1.5, 2], [2, 1]])
plt.scatter(centers[:, 0], centers[:, 1], c='red', s=200, alpha=0.75, marker='X')

plt.title('Clustering Example')
plt.xlabel('Feature 1')
plt.ylabel('Feature 2')
plt.grid(True)
plt.savefig('./labs-sources/images/clustering-example.png')
plt.show() 