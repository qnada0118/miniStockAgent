import os

from dotenv import load_dotenv


def load_app_env():
    """Load .env and remove optional AWS settings when they are blank."""
    load_dotenv()

    if os.environ.get("AWS_PROFILE", "").strip() == "":
        os.environ.pop("AWS_PROFILE", None)

    aws_region = os.environ.get("AWS_REGION", "").strip()
    if aws_region and not os.environ.get("AWS_DEFAULT_REGION"):
        os.environ["AWS_DEFAULT_REGION"] = aws_region
