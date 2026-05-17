from src.data_loader import load_plots
from src.enmap_loader import read_spectral_image_info


def main():
    """
    Test if we can read the EnMap SPECTRAL_IMAGE.TIF
    for every plot.
    """

    plots = load_plots()

    for plot in plots:
        print("Reading EnMap data for:", plot["name"])

        info = read_spectral_image_info(plot)

        print("Plot ID:", info["plot_id"])
        print("Image path:", info["spectral_image_path"])
        print("Bands:", info["band_count"])
        print("Width:", info["width"])
        print("Height:", info["height"])
        print("CRS:", info["crs"])
        print("Bounds:", info["bounds"])
        print("NoData:", info["nodata"])
        print("-" * 60)


if __name__ == "__main__":
    main()