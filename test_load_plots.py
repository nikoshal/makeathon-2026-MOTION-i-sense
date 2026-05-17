from src.data_loader import load_plots


def main():
    """
    Test script to check if plot data loads correctly.
    """

    plots = load_plots()

    print("Number of plots loaded:", len(plots))
    print()

    for plot in plots:
        print("Plot ID:", plot["plot_id"])
        print("Name:", plot["name"])
        print("Latitude:", plot["latitude"])
        print("Longitude:", plot["longitude"])
        print("Area m2:", plot["area_m2"])
        print("Assumed price EUR:", plot["assumed_price_eur"])
        print("-" * 40)


if __name__ == "__main__":
    main()