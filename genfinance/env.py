import os

from dotenv import load_dotenv


def load_app_env():
    """Load .env and remove optional AWS settings when they are blank."""
    load_dotenv()

    if os.environ.get("AWS_PROFILE", "").strip() == "":
        os.environ.pop("AWS_PROFILE", None)
