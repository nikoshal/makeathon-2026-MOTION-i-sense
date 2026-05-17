import pandas as pd

from src.config import FINANCIAL_DATA_DIR


def get_financial_folder_path(crop):
    """
    Return the folder path that contains the financial CSV files for one crop.
    """

    financial_folder = crop["financial_folder"]
    return FINANCIAL_DATA_DIR / financial_folder


def load_csv_file(file_path):
    """
    Load a CSV file into a pandas DataFrame.
    """

    return pd.read_csv(file_path)


def load_financial_data_for_crop(crop):
    """
    Load all financial CSV files for one crop.

    Expected files:
    - crop_economics_inputs.csv
    - yield_ramp_up.csv
    - price_scenarios.csv
    - cost_breakdown.csv
    """

    folder_path = get_financial_folder_path(crop)

    inputs_path = folder_path / "crop_economics_inputs.csv"
    ramp_up_path = folder_path / "yield_ramp_up.csv"
    price_scenarios_path = folder_path / "price_scenarios.csv"
    cost_breakdown_path = folder_path / "cost_breakdown.csv"

    financial_data = {
        "crop_name": crop["name"],
        "folder_path": str(folder_path),
        "inputs": load_csv_file(inputs_path),
        "yield_ramp_up": load_csv_file(ramp_up_path),
        "price_scenarios": load_csv_file(price_scenarios_path),
        "cost_breakdown": load_csv_file(cost_breakdown_path),
    }

    return financial_data