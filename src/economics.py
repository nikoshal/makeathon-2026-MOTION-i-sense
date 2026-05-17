import numpy as np
import numpy_financial as npf


def get_first_row_value(df, column_name):
    """
    Get value from the first row of a DataFrame.
    """

    return df.iloc[0][column_name]


def calculate_yield_factor(suitability_score, crop):
    """
    Convert EnMap suitability score into yield adjustment factor.

    The suitability affects production volume, not profit directly.
    """

    sensitivity = crop.get("yield_sensitivity_to_suitability", 0.7)
    minimum_yield_factor = crop.get("minimum_yield_factor", 0.25)

    yield_factor = 1 - sensitivity * (1 - suitability_score)

    return max(minimum_yield_factor, yield_factor)


def get_ramp_up_factor(ramp_up_df, year_number):
    """
    Get yield ramp-up factor for a specific year.

    If the requested year is beyond the ramp-up table,
    use the last available ramp-up factor.
    """

    matching_rows = ramp_up_df[ramp_up_df["year_number"] == year_number]

    if len(matching_rows) > 0:
        return float(matching_rows.iloc[0]["yield_ramp_up_factor"])

    return float(ramp_up_df["yield_ramp_up_factor"].iloc[-1])


def build_cashflow_table(financial_data, crop, suitability_score, scenario_multiplier=1.0):
    """
    Build year-by-year cashflow table for one crop and one suitability score.
    """

    inputs = financial_data["inputs"]
    ramp_up = financial_data["yield_ramp_up"]

    area_ha = float(get_first_row_value(inputs, "area_ha"))
    full_yield_per_ha = float(get_first_row_value(inputs, "full_yield_per_ha"))
    base_price = float(get_first_row_value(inputs, "base_price_per_unit_eur"))
    annual_opex = float(get_first_row_value(inputs, "annual_opex_eur"))
    total_initial_investment = float(get_first_row_value(inputs, "total_initial_investment_eur"))
    horizon_years = int(get_first_row_value(inputs, "analysis_horizon_years"))
    start_year = int(get_first_row_value(inputs, "start_year"))

    adjusted_price = base_price * scenario_multiplier
    yield_factor = calculate_yield_factor(suitability_score, crop)

    rows = []

    # Year 0: initial investment
    rows.append(
        {
            "year_number": 0,
            "calendar_year": start_year - 1,
            "yield_ramp_up_factor": 0.0,
            "suitability_yield_factor": yield_factor,
            "production_units": 0.0,
            "price_per_unit_eur": adjusted_price,
            "revenue_eur": 0.0,
            "opex_eur": 0.0,
            "cashflow_eur": -total_initial_investment,
        }
    )

    for year_number in range(1, horizon_years + 1):
        calendar_year = start_year + year_number - 1
        ramp_factor = get_ramp_up_factor(ramp_up, year_number)

        production_units = (
            area_ha
            * full_yield_per_ha
            * ramp_factor
            * yield_factor
        )

        revenue = production_units * adjusted_price
        cashflow = revenue - annual_opex

        rows.append(
            {
                "year_number": year_number,
                "calendar_year": calendar_year,
                "yield_ramp_up_factor": ramp_factor,
                "suitability_yield_factor": yield_factor,
                "production_units": production_units,
                "price_per_unit_eur": adjusted_price,
                "revenue_eur": revenue,
                "opex_eur": annual_opex,
                "cashflow_eur": cashflow,
            }
        )

    cumulative = 0.0
    for row in rows:
        cumulative += row["cashflow_eur"]
        row["cumulative_cashflow_eur"] = cumulative

    return rows


def calculate_npv(cashflows, discount_rate):
    """
    Calculate NPV from cashflows.
    """

    return float(npf.npv(discount_rate, cashflows))


def calculate_irr(cashflows):
    """
    Calculate IRR from cashflows.
    """

    irr = npf.irr(cashflows)

    if np.isnan(irr):
        return None

    return float(irr)


def calculate_payback_year(cashflow_table):
    """
    Find first year where cumulative cashflow becomes positive.
    """

    for row in cashflow_table:
        if row["cumulative_cashflow_eur"] >= 0:
            return row["calendar_year"]

    return None


def calculate_financial_summary(financial_data, crop, suitability_score, scenario_name, scenario_multiplier):
    """
    Calculate full financial summary for one price scenario.
    """

    inputs = financial_data["inputs"]
    discount_rate = float(get_first_row_value(inputs, "discount_rate"))

    area_ha = float(get_first_row_value(inputs, "area_ha"))
    full_yield_per_ha = float(get_first_row_value(inputs, "full_yield_per_ha"))
    base_price = float(get_first_row_value(inputs, "base_price_per_unit_eur"))
    annual_opex = float(get_first_row_value(inputs, "annual_opex_eur"))
    total_initial_investment = float(get_first_row_value(inputs, "total_initial_investment_eur"))

    yield_factor = calculate_yield_factor(
        suitability_score=suitability_score,
        crop=crop,
    )

    full_production_units = area_ha * full_yield_per_ha
    adjusted_full_production_units = full_production_units * yield_factor

    cashflow_table = build_cashflow_table(
        financial_data=financial_data,
        crop=crop,
        suitability_score=suitability_score,
        scenario_multiplier=scenario_multiplier,
    )

    cashflows = [row["cashflow_eur"] for row in cashflow_table]

    npv = calculate_npv(cashflows, discount_rate)
    irr = calculate_irr(cashflows)
    payback_year = calculate_payback_year(cashflow_table)

    total_revenue = sum(row["revenue_eur"] for row in cashflow_table)
    total_opex = sum(row["opex_eur"] for row in cashflow_table)
    net_profit = sum(cashflows)

    return {
        "scenario_name": scenario_name,
        "scenario_multiplier": scenario_multiplier,

        "discount_rate": discount_rate,
        "base_price_per_unit_eur": base_price,
        "adjusted_price_per_unit_eur": base_price * scenario_multiplier,

        "area_ha": area_ha,
        "full_yield_per_ha": full_yield_per_ha,
        "full_production_units": full_production_units,
        "suitability_yield_factor": yield_factor,
        "adjusted_full_production_units": adjusted_full_production_units,

        "annual_opex_eur": annual_opex,
        "total_initial_investment_eur": total_initial_investment,

        "npv_eur": npv,
        "irr": irr,
        "payback_year": payback_year,
        "total_revenue_eur": total_revenue,
        "total_opex_eur": total_opex,
        "net_profit_eur": net_profit,

        "cashflow_table": cashflow_table,
    }