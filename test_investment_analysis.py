from src.data_loader import load_plots, load_crop_knowledge_base
from src.investment_analysis import build_full_investment_analysis


def main():
    plots = load_plots()
    crops = load_crop_knowledge_base()

    results = build_full_investment_analysis(
        plots=plots,
        crops=crops,
        investor_risk_level="medium",
    )

    print()
    print("Top 10 investment results by NPV")
    print("-" * 100)

    for row in results[:10]:
        irr_text = "N/A" if row["irr"] is None else f"{row['irr']:.2%}"

        print(
            f"Rank {row['rank_by_npv']}: "
            f"{row['plot_name']} + {row['crop_name']} "
            f"({row['scenario_name']}) | "
            f"NPV: {row['npv_eur']:,.2f} EUR | "
            f"IRR: {irr_text} | "
            f"Payback: {row['payback_year']} | "
            f"Suitability: {row['suitability_score']}"
        )


if __name__ == "__main__":
    main()