import matplotlib.pyplot as plt
import numpy as np

# Generate sample data
np.random.seed(42)
data1 = np.random.normal(0, 1, 100)
data2 = np.random.normal(1, 1.5, 100)
data3 = np.random.normal(2, 1, 100)

# Combine data into a list
data = [data1, data2, data3]
labels = ['Group 1', 'Group 2', 'Group 3']

# Create the boxplot
fig, ax = plt.subplots()
box = ax.boxplot(data, patch_artist=True, labels=labels)

# Customize boxplot colors for legend
colors = ['skyblue', 'lightgreen', 'salmon']
for patch, color in zip(box['boxes'], colors):
    patch.set_facecolor(color)

# Add a legend
legend_labels = ['Dataset 1', 'Dataset 2', 'Dataset 3']
handles = [plt.Line2D([0], [0], color=color, lw=4) for color in colors]
ax.legend(handles, legend_labels, title='Datasets', loc='upper right')

# Set labels and title
ax.set_title('Boxplot with Legend')
ax.set_ylabel('Execution (Ms)')
ax.set_xlabel('Operation')

# Show the plot
plt.show()
