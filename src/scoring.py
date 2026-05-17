def score_ph_suitability(estimated_ph, crop):
    """
    Score how well the estimated plot pH fits the crop pH range.

    Returns score from 0 to 1.
    1 = perfect fit
    0 = bad fit
    """

    ph_min = crop["suitable_ph_min"]
    ph_max = crop["suitable_ph_max"]

    if ph_min <= estimated_ph <= ph_max:
        return 1.0

    # If pH is outside the ideal range, calculate distance.
    if estimated_ph < ph_min:
        distance = ph_min - estimated_ph
    else:
        distance = estimated_ph - ph_max

    # Small distance = smaller penalty.
    score = max(0.0, 1.0 - distance / 2.0)

    return round(score, 3)


def score_water_suitability(ndmi_mean, crop):
    """
    Score water suitability using NDMI and crop water sensitivity.

    NDMI is used as moisture proxy.
    Higher NDMI = better moisture condition.
    """

    # Normalize NDMI roughly into 0-1 range.
    # This is simple MVP logic.
    moisture_score = (ndmi_mean + 0.2) / 0.8
    moisture_score = max(0.0, min(1.0, moisture_score))

    water_sensitivity = crop["water_risk_sensitivity"]

    # If crop is sensitive to water risk, low moisture hurts more.
    penalty = water_sensitivity * (1.0 - moisture_score)

    score = 1.0 - penalty

    return round(max(0.0, min(1.0, score)), 3)


def score_vegetation_suitability(ndvi_mean):
    """
    Score general vegetation/land productivity proxy from NDVI.

    Higher NDVI generally indicates better vegetation condition.
    """

    # Normalize NDVI into 0-1.
    score = ndvi_mean / 0.8

    return round(max(0.0, min(1.0, score)), 3)


def score_risk_fit(crop, investor_risk_level):
    """
    Score how well crop risk matches investor risk tolerance.

    Low-risk investor dislikes high-risk crops.
    High-risk investor accepts them more.
    """

    avg_risk = (
        crop["regulatory_risk_score"]
        + crop["market_risk_score"]
        + crop["climate_risk_score"]
        + crop["capex_risk_score"]
    ) / 4

    if investor_risk_level == "low":
        score = 1.0 - avg_risk
    elif investor_risk_level == "medium":
        score = 1.0 - abs(avg_risk - 0.5)
    elif investor_risk_level == "high":
        score = 0.5 + avg_risk / 2
    else:
        score = 1.0 - avg_risk

    return round(max(0.0, min(1.0, score)), 3)


def calculate_crop_plot_suitability(plot_indices, crop, investor_risk_level="medium"):
    """
    Combine pH, moisture, vegetation and risk scores into one suitability score.
    """

    estimated_ph = plot_indices["ph_proxy"]["estimated_ph"]
    ndmi_mean = plot_indices["ndmi"]["mean"]
    ndvi_mean = plot_indices["ndvi"]["mean"]

    ph_score = score_ph_suitability(estimated_ph, crop)
    water_score = score_water_suitability(ndmi_mean, crop)
    vegetation_score = score_vegetation_suitability(ndvi_mean)
    risk_score = score_risk_fit(crop, investor_risk_level)

    # Balanced MVP weights.
    overall_score = (
        0.25 * ph_score
        + 0.30 * water_score
        + 0.25 * vegetation_score
        + 0.20 * risk_score
    )

    return {
        "ph_score": ph_score,
        "water_score": water_score,
        "vegetation_score": vegetation_score,
        "risk_score": risk_score,
        "overall_suitability_score": round(overall_score, 3),
    }
