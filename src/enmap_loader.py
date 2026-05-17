import rasterio

from src.config import ENMAP_DIR


def get_enmap_paths(plot):
    """
    Given one plot dictionary, return the paths to its EnMap files.
    """

    plot_folder = ENMAP_DIR / plot["enmap_folder"]

    spectral_image_path = plot_folder / "SPECTRAL_IMAGE.TIF"
    metadata_path = plot_folder / "METADATA.XML"

    return {
        "plot_folder": plot_folder,
        "spectral_image": spectral_image_path,
        "metadata": metadata_path,
    }


def read_spectral_image_info(plot):
    """
    Open the EnMap SPECTRAL_IMAGE.TIF and return basic information.

    This does not yet calculate NDVI etc.
    It only checks if Python can read the satellite file.
    """

    paths = get_enmap_paths(plot)

    with rasterio.open(paths["spectral_image"]) as dataset:
        info = {
            "plot_id": plot["plot_id"],
            "plot_name": plot["name"],
            "spectral_image_path": str(paths["spectral_image"]),
            "band_count": dataset.count,
            "width": dataset.width,
            "height": dataset.height,
            "crs": str(dataset.crs),
            "bounds": dataset.bounds,
            "nodata": dataset.nodata,
        }

    return info