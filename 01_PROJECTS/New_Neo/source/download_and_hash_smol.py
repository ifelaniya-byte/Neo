# download_and_hash_smol.py
import os
import hashlib
import urllib.request

MODEL_URL = "https://huggingface.co/HuggingFaceTB/SmolLM2-1.7B-Instruct-GGUF/resolve/main/smollm2-1.7b-instruct-q4_k_m.gguf"
TARGET_DIR = "C:\\Users\\AIAli\\OneDrive\\Desktop\\NEO\\models"
TARGET_PATH = os.path.join(TARGET_DIR, "smollm2-1.7b-instruct-q4_k_m.gguf")

# Ensure directory exists
os.makedirs(TARGET_DIR, exist_ok=True)

def download_file(url: str, path: str):
    print(f"Downloading SmolLM2-1.7B-Instruct (Q4_K_M) to {path}...")
    print("This is a ~1.06 GB download. Please wait...")
    
    def report_hook(block_num, block_size, total_size):
        downloaded = block_num * block_size
        percent = min(100, (downloaded / total_size) * 100) if total_size > 0 else 0
        print(f"\rProgress: {percent:.2f}% ({downloaded / (1024**2):.1f} MB / {total_size / (1024**2):.1f} MB)", end="")

    urllib.request.urlretrieve(url, path, reporthook=report_hook)
    print("\nDownload complete!")

def compute_sha256(path: str) -> str:
    print("Computing SHA-256 checksum...")
    sha256_hash = hashlib.sha256()
    with open(path, "rb") as f:
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

if __name__ == "__main__":
    if not os.path.exists(TARGET_PATH):
        download_file(MODEL_URL, TARGET_PATH)
    else:
        print(f"Model file already exists at {TARGET_PATH}")
        
    hash_val = compute_sha256(TARGET_PATH)
    print(f"\nTOFU SHA-256 Pin: {hash_val}")
    print("Save this hash to your verified pipeline config registry.")
