import os


class Config:
    """Application configuration."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "aktu-college-predictor-secret-key")
    DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "aktu_cutoff.csv")
    ANALYTICS_FILE = os.path.join(os.path.dirname(__file__), "data", "analytics.json")
    ADMIN_KEY = os.environ.get("ADMIN_KEY", "admin123")
