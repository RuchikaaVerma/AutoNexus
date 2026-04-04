from huggingface_hub import HfApi

api = HfApi()

REPO_ID = "divyanshi-02/autonexus-p2-ml-models"
TOKEN = "your_new_token_here"  # ⚠️ use new token

files = [
    "models/anomaly_detector.pkl",
    "models/brake_failure_model.pkl",
    "models/demand_forecaster.pkl",
    "models/label_encoder.pkl"
]

for file in files:
    api.upload_file(
        path_or_fileobj=file,
        path_in_repo=file.split("/")[-1],  # just filename
        repo_id=REPO_ID,
        token=TOKEN
    )

print("All models uploaded successfully 🚀")