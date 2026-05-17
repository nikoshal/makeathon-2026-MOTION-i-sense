from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
ENMAP_DIR = DATA_DIR / "enmap"
FINANCIAL_DATA_DIR = DATA_DIR / "financial_data"

PLOTS_FILE = DATA_DIR / "plots.json"
CROP_KNOWLEDGE_BASE_FILE = DATA_DIR / "crop_knowledge_base.json"