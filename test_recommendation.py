from src.data_loader import load_plots, load_crop_knowledge_base
from src.recommendation import build_recommendation_table


def main():
    plots = load_plots()
    crops = load_crop_knowledge_base()

    recommendations = build_recommendation_table(
        plots=plots,
        crops=crops,
        investor_risk_level="medium",
    )

    print("Top 10 recommendations")
    print("-" * 80)

    for row in recommendations[:10]:
        print(
            f"Rank {row['rank']}: "
            f"{row['plot_name']} + {row['crop_name']} "
            f"| score: {row['overall_suitability_score']} "
            f"| pH: {row['estimated_ph']} ({row['ph_class']}) "
            f"| NDVI: {row['ndvi_mean']} "
            f"| NDMI: {row['ndmi_mean']}"
        )


if __name__ == "__main__":
    main()