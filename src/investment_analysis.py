from src.spectral_indices import compute_spectral_indices_for_plot
from src.scoring import calculate_crop_plot_suitability
from src.financial_loader import load_financial_data_for_crop
from src.economics import calculate_financial_summary


def build_full_investment_analysis(plots, crops, investor_risk_level="medium"):
    """
    Build full investment analysis for all plot + crop + scenario combinations.
    """

    results = []

    for plot in plots:
        print(f"Processing plot: {plot['name']}")

        plot_indices = compute_spectral_indices_for_plot(plot)

        for crop in crops:
            print(f"  Processing crop: {crop['name']}")

            suitability = calculate_crop_plot_suitability(
                plot_indices=plot_indices,
                crop=crop,
                investor_risk_level=investor_risk_level,
            )

            suitability_score = suitability["overall_suitability_score"]

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

                row = {
                    "plot_id": plot["plot_id"],
                    "plot_name": plot["name"],
                    "crop_id": crop["scenario_id"],
                    "crop_name": crop["name"],
                    "scenario_name": summary["scenario_name"],

                    "suitability_score": suitability_score,
                    "ph_score": suitability["ph_score"],
                    "water_score": suitability["water_score"],
                    "vegetation_score": suitability["vegetation_score"],
                    "risk_score": suitability["risk_score"],

                    "estimated_ph": plot_indices["ph_proxy"]["estimated_ph"],
                    "ph_class": plot_indices["ph_proxy"]["ph_class"],
                    "ndvi_mean": round(plot_indices["ndvi"]["mean"], 4),
                    "ndmi_mean": round(plot_indices["ndmi"]["mean"], 4),

                    "scenario_multiplier": summary["scenario_multiplier"],
                    "discount_rate": summary["discount_rate"],
                    "npv_eur": summary["npv_eur"],
                    "irr": summary["irr"],
                    "payback_year": summary["payback_year"],
                    "total_revenue_eur": summary["total_revenue_eur"],
                    "total_opex_eur": summary["total_opex_eur"],
                    "net_profit_eur": summary["net_profit_eur"],

                    "cashflow_table": summary["cashflow_table"],
                    
                    "area_ha": summary["area_ha"],
                    "full_yield_per_ha": summary["full_yield_per_ha"],
                    "full_production_units": summary["full_production_units"],
                    "suitability_yield_factor": summary["suitability_yield_factor"],
                    "adjusted_full_production_units": summary["adjusted_full_production_units"],
                    "base_price_per_unit_eur": summary["base_price_per_unit_eur"],
                    "adjusted_price_per_unit_eur": summary["adjusted_price_per_unit_eur"],
                    "annual_opex_eur": summary["annual_opex_eur"],
                    "total_initial_investment_eur": summary["total_initial_investment_eur"],
                }

                results.append(row)

    results = sorted(
        results,
        key=lambda row: row["npv_eur"],
        reverse=True,
    )

    for index, row in enumerate(results, start=1):
        row["rank_by_npv"] = index

    return results