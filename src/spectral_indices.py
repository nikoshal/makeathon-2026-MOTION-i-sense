import numpy as np
import rasterio
import xml.etree.ElementTree as ET

from src.enmap_loader import get_enmap_paths


def parse_band_metadata(metadata_path):
    """
    Read METADATA.XML and return only the spectral bands
    that contain wavelength information.
    """

    tree = ET.parse(metadata_path)
    root = tree.getroot()

    bands = []

    for band_element in root.findall(".//bandID"):
        wavelength_text = band_element.findtext("wavelengthCenterOfBand")

        # Some bandID elements may not contain wavelength info.
        # We skip them.
        if wavelength_text is None:
            continue

        band_number = int(band_element.attrib["number"])
        wavelength = float(wavelength_text)

        gain_text = band_element.findtext("GainOfBand")
        offset_text = band_element.findtext("OffsetOfBand")

        gain = float(gain_text) if gain_text is not None else 1.0
        offset = float(offset_text) if offset_text is not None else 0.0

        bands.append(
            {
                "band_number": band_number,
                "wavelength": wavelength,
                "gain": gain,
                "offset": offset,
            }
        )

    return bands

def find_closest_band(bands, target_wavelength):
    """
    Find the EnMap band closest to a target wavelength.
    Example: target_wavelength = 665 for Red.
    """

    closest_band = min(
        bands,
        key=lambda band: abs(band["wavelength"] - target_wavelength)
    )

    return closest_band


def read_reflectance_band(dataset, band_info):
    """
    Read one band from SPECTRAL_IMAGE.TIF and apply gain/offset.

    EnMap metadata gives GainOfBand.
    Reflectance ≈ raw_value * gain + offset.
    """

    raw = dataset.read(band_info["band_number"]).astype("float32")

    reflectance = raw * band_info["gain"] + band_info["offset"]

    if dataset.nodata is not None:
        reflectance = np.where(raw == dataset.nodata, np.nan, reflectance)

    return reflectance


def safe_index(numerator, denominator):
    """
    Safely calculate spectral index.
    Avoid division by zero.
    """

    return np.where(
        denominator == 0,
        np.nan,
        numerator / denominator
    )


def summarize_array(array):
    """
    Return mean, min and max ignoring NaN values.
    """

    return {
        "mean": float(np.nanmean(array)),
        "min": float(np.nanmin(array)),
        "max": float(np.nanmax(array)),
    }


def estimate_ph_proxy(ndvi_mean, ndmi_mean, brightness_mean, redness_mean, swir_ratio_mean):
    """
    Rough rule-based pH proxy.

    Important:
    This is NOT laboratory pH.
    It is an educated hyperspectral assumption for MVP functionality.
    """

    # Start from a neutral-to-slightly-alkaline Mediterranean default.
    estimated_ph = 7.2

    # Brighter/drier/calcareous-looking soils tend to push alkaline assumption upward.
    estimated_ph += (brightness_mean - 0.20) * 1.2

    # Lower moisture can indicate drier/calcareous surface tendency.
    estimated_ph += (0.15 - ndmi_mean) * 0.6

    # Redness can indicate iron oxide / mineral surface effects.
    estimated_ph += (redness_mean - 1.0) * 0.25

    # SWIR ratio used as rough mineral/soil surface proxy.
    estimated_ph += (swir_ratio_mean - 1.0) * 0.35

    # Dense vegetation makes soil pH inference less reliable;
    # pull estimate slightly back toward neutral.
    if ndvi_mean > 0.55:
        estimated_ph -= 0.2

    # Keep result in a plausible agricultural soil range.
    estimated_ph = float(np.clip(estimated_ph, 5.5, 8.5))

    if estimated_ph < 6.5:
        ph_class = "slightly_acidic"
    elif estimated_ph < 7.3:
        ph_class = "neutral"
    elif estimated_ph < 8.0:
        ph_class = "slightly_alkaline"
    else:
        ph_class = "alkaline"

    return {
        "estimated_ph": round(estimated_ph, 2),
        "ph_class": ph_class,
        "ph_confidence": "low_to_medium",
        "ph_method": "rule_based_hyperspectral_proxy_not_lab_measurement",
    }


def compute_spectral_indices_for_plot(plot):
    """
    Compute EnMap-based indicators for one plot.
    """

    paths = get_enmap_paths(plot)

    bands = parse_band_metadata(paths["metadata"])

    red_band = find_closest_band(bands, 665)
    green_band = find_closest_band(bands, 560)
    blue_band = find_closest_band(bands, 490)
    nir_band = find_closest_band(bands, 842)
    swir1_band = find_closest_band(bands, 1610)
    swir2_band = find_closest_band(bands, 2200)

    with rasterio.open(paths["spectral_image"]) as dataset:
        red = read_reflectance_band(dataset, red_band)
        green = read_reflectance_band(dataset, green_band)
        blue = read_reflectance_band(dataset, blue_band)
        nir = read_reflectance_band(dataset, nir_band)
        swir1 = read_reflectance_band(dataset, swir1_band)
        swir2 = read_reflectance_band(dataset, swir2_band)

    ndvi = safe_index(nir - red, nir + red)
    ndmi = safe_index(nir - swir1, nir + swir1)

    brightness = np.nanmean(
        np.stack([red, green, blue]),
        axis=0
    )

    redness_proxy = safe_index(
        red,
        (green + blue) / 2
    )

    swir_ratio_proxy = safe_index(
        swir1,
        swir2
    )

    ndvi_summary = summarize_array(ndvi)
    ndmi_summary = summarize_array(ndmi)
    brightness_summary = summarize_array(brightness)
    redness_summary = summarize_array(redness_proxy)
    swir_ratio_summary = summarize_array(swir_ratio_proxy)

    ph_proxy = estimate_ph_proxy(
        ndvi_mean=ndvi_summary["mean"],
        ndmi_mean=ndmi_summary["mean"],
        brightness_mean=brightness_summary["mean"],
        redness_mean=redness_summary["mean"],
        swir_ratio_mean=swir_ratio_summary["mean"],
    )

    return {
        "plot_id": plot["plot_id"],
        "plot_name": plot["name"],

        "bands_used": {
            "red": red_band,
            "green": green_band,
            "blue": blue_band,
            "nir": nir_band,
            "swir1": swir1_band,
            "swir2": swir2_band,
        },

        "ndvi": ndvi_summary,
        "ndmi": ndmi_summary,
        "brightness": brightness_summary,
        "redness_proxy": redness_summary,
        "swir_ratio_proxy": swir_ratio_summary,

        "ph_proxy": ph_proxy,
    }