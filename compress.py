import numpy as np
X = np.load('data/X_conv_sequences.npy')
np.save('data/X_conv_sequences_fp16.npy', X.astype('float16'))
print('done')