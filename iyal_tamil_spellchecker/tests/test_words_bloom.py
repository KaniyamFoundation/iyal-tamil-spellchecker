import pickle
import os
BLOOM_PATH = "tamil_bloom.pkl"

with open(BLOOM_PATH, "rb") as f:
    bloom = pickle.load(f)

words = ["பஸ்ஸில்", "டிக்கெட்டை"]
for word in words:
    print(f"'{word}' in bloom: {word in bloom}")
