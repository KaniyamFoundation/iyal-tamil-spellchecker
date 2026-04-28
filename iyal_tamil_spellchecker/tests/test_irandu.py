import pickle
import os
BLOOM_PATH = "tamil_bloom.pkl"

with open(BLOOM_PATH, "rb") as f:
    bloom = pickle.load(f)

word = "இரன்டு"
print(f"'{word}' in bloom: {word in bloom}")
