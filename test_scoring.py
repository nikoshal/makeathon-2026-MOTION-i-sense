from src.data_loader import load_plots, load_crop_knowledge_base
from src.spectral_indices import compute_spectral_indices_for_plot
from src.scoring import calculate_crop_plot_suitability


def main():
    plots = load_plots()
    crops = load_crop_knowledge_base()

    investor_risk_level = "medium"

    for plot in plots:
        print("Plot:", plot["name"])

        plot_indices = compute_spectral_indices_for_plot(plot)

        for crop in crops:
            score = calculate_crop_plot_suitability(
                plot_indices=plot_indices,
                crop=crop,
                investor_risk_level=investor_risk_level,
            )

            print(
                crop["name"],
                "| overall:",
                score["overall_suitability_score"],
                "| pH:",
                score["ph_score"],
                "| water:",
                score["water_score"],
                "| vegetation:",
                score["vegetation_score"],
                "| risk:",
                score["risk_score"],
            )

        print("-" * 70)


if __name__ == "__main__":
    main()