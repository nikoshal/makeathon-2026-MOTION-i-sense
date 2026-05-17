from src.data_loader import load_plots
from src.spectral_indices import compute_spectral_indices_for_plot


def main():
    plots = load_plots()

    for plot in plots:
        print("Computing spectral indices for:", plot["name"])

        result = compute_spectral_indices_for_plot(plot)

        print("Plot ID:", result["plot_id"])
        print("NDVI mean:", round(result["ndvi"]["mean"], 4))
        print("NDMI mean:", round(result["ndmi"]["mean"], 4))
        print("Brightness mean:", round(result["brightness"]["mean"], 4))
        print("Redness proxy mean:", round(result["redness_proxy"]["mean"], 4))
        print("SWIR ratio proxy mean:", round(result["swir_ratio_proxy"]["mean"], 4))

        print("Estimated pH:", result["ph_proxy"]["estimated_ph"])
        print("pH class:", result["ph_proxy"]["ph_class"])
        print("pH confidence:", result["ph_proxy"]["ph_confidence"])

        print("Bands used:")
        for band_name, band_info in result["bands_used"].items():
            print(
                f"  {band_name}: band {band_info['band_number']} "
                f"({band_info['wavelength']:.1f} nm)"
            )

        print("-" * 60)


if __name__ == "__main__":
    main()