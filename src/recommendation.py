from src.spectral_indices import compute_spectral_indices_for_plot
from src.scoring import calculate_crop_plot_suitability


def build_recommendation_table(plots, crops, investor_risk_level="medium"):
    """
    Build a ranked recommendation table for all plot + crop combinations.
    """

    results = []

    for plot in plots:
        plot_indices = compute_spectral_indices_for_plot(plot)

        for crop in crops:
            scores = calculate_crop_plot_suitability(
                plot_indices=plot_indices,
                crop=crop,
                investor_risk_level=investor_risk_level,
            )

            row = {
                "plot_id": plot["plot_id"],
                "plot_name": plot["name"],
                "crop_id": crop["scenario_id"],
                "crop_name": crop["name"],

                "overall_suitability_score": scores["overall_suitability_score"],
                "ph_score": scores["ph_score"],
                "water_score": scores["water_score"],
                "vegetation_score": scores["vegetation_score"],
                "risk_score": scores["risk_score"],

                "estimated_ph": plot_indices["ph_proxy"]["estimated_ph"],
                "ph_class": plot_indices["ph_proxy"]["ph_class"],
                "ph_confidence": plot_indices["ph_proxy"]["ph_confidence"],

                "ndvi_mean": round(plot_indices["ndvi"]["mean"], 4),
                "ndmi_mean": round(plot_indices["ndmi"]["mean"], 4),
                "brightness_mean": round(plot_indices["brightness"]["mean"], 4),

                "crop_notes": crop["notes"],
            }

            results.append(row)

    results = sorted(
        results,
        key=lambda row: row["overall_suitability_score"],
        reverse=True,
    )

    for index, row in enumerate(results, start=1):
        row["rank"] = index

    return results


def get_best_crop_for_plot(recommendation_table, plot_name):
    """
    Return the best crop for a selected plot.
    """

    filtered = [
        row for row in recommendation_table
        if row["plot_name"] == plot_name
    ]

    if not filtered:
        return None

    return filtered[0]