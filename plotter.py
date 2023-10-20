"""
Reads in sensor_data csv and plots, called from plot button of GUI
"""

import pandas as pd
import matplotlib.pyplot as plt


def plot_sensor_data(detail_level="Low"):
    plt.close("all")
    # Load data
    data = pd.read_csv("sensor_data.csv")
    # data = pd.read_csv("fake_sensor_data.csv") # for testing

    # Generate relative time in seconds given the sample rate
    sample_rate = 80  # Hz
    data["Relative Time"] = data.index * (1 / sample_rate)

    # Convert columns to numeric, coercing errors to NaN
    data[["X", "Y", "Z"]] = data[["X", "Y", "Z"]].apply(pd.to_numeric, errors="coerce")

    # Optionally, handle NaN values - e.g., drop them
    data = data.dropna(subset=["X", "Y", "Z"])

    # Set "Relative Time" as index
    data.set_index("Relative Time", inplace=True)
    # Sample at n-intervals based on detail level

    num_rows = len(data)
    if detail_level == "High":
        n = max(1, num_rows // 1000000)
    elif detail_level == "Low":
        n = max(10, num_rows // 100000)
    else:  # Default to "Medium"
        n = max(5, num_rows // 500000)

    data = data.drop(columns=["Time"])

    sampled = data.iloc[::n]

    window_size = 80  # This would be equivalent to 1 second at 80Hz

    if num_rows > 100000:
        window_size = 72000  # approx 15min window intervals for larger datasets

    downsampled = sampled.rolling(window=window_size).mean()

    # plot_data = sampled
    plot_data = downsampled

    # Plot sampled data
    time_scaling = 3600 #in terms of relative hours

    plt.plot(
        plot_data.index / time_scaling, plot_data["X"], label="X"
    )  # scale relative time to hours
    plt.plot(plot_data.index / time_scaling, plot_data["Y"], label="Y")
    plt.plot(plot_data.index / time_scaling, plot_data["Z"], label="Z")

    # # Plot data
    # plt.plot(data["Relative Time"], data["X"], label="X")
    # plt.plot(data["Relative Time"], data["Y"], label="Y")
    # plt.plot(data["Relative Time"], data["Z"], label="Z")

    # Label axes
    plt.xlabel("Relative Time (h)")
    plt.ylabel("Magnetic Field (mG)")

    # Add title and legend
    plt.title("Magnetic Field vs Relative Time")
    plt.grid()
    plt.legend()
    plt.tight_layout()

    # Display plot
    plt.show()


# plot_sensor_data() # for testing
