"""Script to download and save all-MiniLM-L6-v2 model locally for 100% offline inference."""
import os
from sentence_transformers import SentenceTransformer

TARGET_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "models",
    "all-MiniLM-L6-v2",
)


def main():
    print(f"Downloading and saving embedding model to {TARGET_DIR}...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    model.save(TARGET_DIR)
    print(f"Successfully saved embedding model to {TARGET_DIR} for offline use.")


if __name__ == "__main__":
    main()

