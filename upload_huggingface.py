from huggingface_hub import HfApi

api = HfApi()

REPO_ID = "divyanshi-02/autonexus-p2-ml-models"
TOKEN = "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"  # ⚠️ use new token

files = [
    "anomaly_detector.pkl",
    "brake_failure_model.pkl",
    "demand_forecaster.pkl",
    "label_encoder.pkl"
]

for file in files:
    api.upload_file(
        path_or_fileobj=file,
        path_in_repo=file.split("/")[-1],  # just filename
        repo_id=REPO_ID,
        token=TOKEN
    )

print("All models uploaded successfully 🚀")