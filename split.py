import numpy as np

X = np.load('data/X_conv_sequences_fp16.npy')
y = np.load('data/y_conv_labels.npy')

mid = len(X) // 2

np.save('data/X_conv_part1.npy', X[:mid])
np.save('data/X_conv_part2.npy', X[mid:])
np.save('data/y_conv_part1.npy', y[:mid])
np.save('data/y_conv_part2.npy', y[mid:])

print(f"Part 1: {len(X[:mid])} samples")
print(f"Part 2: {len(X[mid:])} samples")