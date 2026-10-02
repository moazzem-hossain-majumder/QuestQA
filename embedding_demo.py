"""
Task 3 helper: embed a sentence with watsonx_embedding() and print the first five numbers.
Take your `embedding.png` screenshot of this file's code + the terminal output.

Usage:
    python embedding_demo.py
    python embedding_demo.py "your own sentence"
"""
import sys

from qabot import watsonx_embedding

DEFAULT_SENTENCE = "Hello this is a test sentence"  # replace with the sentence given in your lab if different

sentence = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SENTENCE
embedder = watsonx_embedding()
vector = embedder.embed_query(sentence)

print(f"Sentence : {sentence}")
print(f"Dimension: {len(vector)}")
print(f"First five embedding numbers: {vector[:5]}")
