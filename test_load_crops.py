from src.data_loader import load_crop_knowledge_base


def main():
    """
    Test script to check if crop / investment scenario data loads correctly.
    """

    crop_scenarios = load_crop_knowledge_base()

    print("Number of crop scenarios loaded:", len(crop_scenarios))
    print()

    for scenario in crop_scenarios:
        print("Scenario ID:", scenario["scenario_id"])
        print("Name:", scenario["name"])
        print("Revenue €/ha/year:", scenario["expected_revenue_eur_per_ha_per_year"])
        print("OPEX €/ha/year:", scenario["expected_opex_eur_per_ha_per_year"])
        print("CAPEX €/ha:", scenario["initial_capex_eur_per_ha"])
        print("Years to maturity:", scenario["years_to_maturity"])
        print("Regulatory risk:", scenario["regulatory_risk_score"])
        print("Market risk:", scenario["market_risk_score"])
        print("-" * 40)


if __name__ == "__main__":
    main()