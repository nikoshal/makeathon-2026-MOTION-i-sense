from src.data_loader import load_crop_knowledge_base
from src.financial_loader import load_financial_data_for_crop


def main():
    crops = load_crop_knowledge_base()

    for crop in crops:
        print("Loading financial data for:", crop["name"])

        data = load_financial_data_for_crop(crop)

        print("Folder:", data["folder_path"])
        print("Inputs rows:", len(data["inputs"]))
        print("Yield ramp-up rows:", len(data["yield_ramp_up"]))
        print("Price scenarios rows:", len(data["price_scenarios"]))
        print("Cost breakdown rows:", len(data["cost_breakdown"]))

        print()
        print("Inputs preview:")
        print(data["inputs"].head())

        print("-" * 80)


if __name__ == "__main__":
    main()