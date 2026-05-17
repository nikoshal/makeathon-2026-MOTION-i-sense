import json
from typing import Any, Dict, List

from src.config import PLOTS_FILE, CROP_KNOWLEDGE_BASE_FILE


def load_json_file(file_path) -> Any:
    """
    Load a JSON file and return its content as Python data.

    JSON array  -> Python list
    JSON object -> Python dictionary
    """

    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data


def load_plots() -> List[Dict[str, Any]]:
    """
    Load the land plots from data/plots.json.

    Returns a list of dictionaries.
    Each dictionary is one land plot.
    """

    plots = load_json_file(PLOTS_FILE)

    return plots


def load_crop_knowledge_base() -> List[Dict[str, Any]]:
    """
    Load crop / investment scenarios from data/crop_knowledge_base.json.

    Returns a list of dictionaries.
    Each dictionary is one crop or investment scenario.
    """

    crop_scenarios = load_json_file(CROP_KNOWLEDGE_BASE_FILE)

    return crop_scenarios