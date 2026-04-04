from huggingface_hub import HfApi, create_repo
import os

print("Uploading Model to Hugging Face...\n")

# Your Hugging Face credentials
HF_USERNAME = "your_token"
HF_TOKEN = "your_token"
MODEL_NAME = "vehicle-failure-predictor"

# Create repo (if doesn't exist)
repo_id = f"{HF_USERNAME}/{MODEL_NAME}"

try:
    create_repo(
        repo_id=repo_id,
        token=HF_TOKEN,
        repo_type="model",
        exist_ok=True
    )
    print(f"✓ Repository created/verified: {repo_id}\n")
except Exception as e:
    print(f"Note: {e}\n")

# Upload model file
api = HfApi()

print("Uploading model file...")
api.upload_file(
    path_or_fileobj="vehicle_failure_model.pkl",
    path_in_repo="vehicle_failure_model.pkl",
    repo_id=repo_id,
    token=HF_TOKEN
)

print(f"✓ Model uploaded successfully!")
print(f"\nModel URL: https://huggingface.co/{repo_id}")
print(f"\nTo download: use repo_id = '{repo_id}'")