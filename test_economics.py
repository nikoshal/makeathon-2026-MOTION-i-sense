from src.data_loader import load_plots, load_crop_knowledge_base
from src.spectral_indices import compute_spectral_indices_for_plot
from src.scoring import calculate_crop_plot_suitability
from src.financial_loader import load_financial_data_for_crop
from src.economics import calculate_financial_summary


def main():
    plots = load_plots()
    crops = load_crop_knowledge_base()

    # Test with first plot and first crop
    plot = plots[0]
    crop = crops[0]

    print("Plot:", plot["name"])
    print("Crop:", crop["name"])

    plot_indices = compute_spectral_indices_for_plot(plot)

    suitability = calculate_crop_plot_suitability(
        plot_indices=plot_indices,
        crop=crop,
        investor_risk_level="medium",
    )

    suitability_score = suitability["overall_suitability_score"]

    print("Suitability score:", suitability_score)

    financial_data = load_financial_data_for_crop(crop)
    price_scenarios = financial_data["price_scenarios"]

    for _, scenario in price_scenarios.iterrows():
        summary = calculate_financial_summary(
            financial_data=financial_data,
            crop=crop,
            suitability_score=suitability_score,
            scenario_name=scenario["scenario_name"],
            scenario_multiplier=float(scenario["price_multiplier"]),
        )

        print()
        print("Scenario:", summary["scenario_name"])
        print("NPV EUR:", round(summary["npv_eur"], 2))
        print("IRR:", None if summary["irr"] is None else round(summary["irr"], 4))
        print("Payback year:", summary["payback_year"])
        print("Total revenue EUR:", round(summary["total_revenue_eur"], 2))
        print("Total OPEX EUR:", round(summary["total_opex_eur"], 2))
        print("Net profit EUR:", round(summary["net_profit_eur"], 2))

        print("First 5 cashflow rows:")
        for row in summary["cashflow_table"][:5]:
            print(row)


if __name__ == "__main__":
    main()