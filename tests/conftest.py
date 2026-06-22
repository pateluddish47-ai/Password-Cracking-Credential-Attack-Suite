import sys
from pathlib import Path

SUITE_DIR = Path(__file__).resolve().parent.parent / "password_suite"
if str(SUITE_DIR) not in sys.path:
    sys.path.insert(0, str(SUITE_DIR))
