from pathlib import Path

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads" / "avatars"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
