"""
Reads in sensor_data csv and plots, called from plot button of GUI
"""

import pandas as pd
import matplotlib.pyplot as plt


def plot_sensor_data(detail_level="Low"):
    plt.close("all")
    fig, ax = plt.subplots(3,1, figsize=(8, 5))
    # Load data
    data = pd.read_csv("sensor_data.csv")
    # data = pd.read_csv("fake_sensor_data.csv") # for testing

    # Generate relative time in seconds given the sample rate
    sample_rate = 155  # Hz
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
        n = max(10, num_rows // 250000)
    else:  # Default to "Medium"
        n = max(5, num_rows // 500000)

    data = data.drop(columns=["Time"])

    sampled = data.iloc[::n]

    window_size = 155  # This would be equivalent to 1 second at 80Hz

    if num_rows > 100000:
        window_size = 72000  # approx 15min window intervals for larger datasets

    downsampled = sampled.rolling(window=window_size).mean()

    # plot_data = sampled
    plot_data = downsampled

    # Plot sampled data
    time_scaling = 3600  # in terms of relative hours

    ax[0].plot(plot_data.index / time_scaling, plot_data["X"], label="X", color='blue')
    ax[1].plot(plot_data.index / time_scaling, plot_data["Y"], label="Y", color='orange')
    ax[2].plot(plot_data.index / time_scaling, plot_data["Z"], label="Z", color='green')

    # # Plot data
    # plt.plot(data["Relative Time"], data["X"], label="X")
    # plt.plot(data["Relative Time"], data["Y"], label="Y")
    # plt.plot(data["Relative Time"], data["Z"], label="Z")

    for a in ax:
        a.grid(True)
        

    # Add title and legend
    fig.suptitle("Magnetic Field vs Relative Time")
    fig.supxlabel("Relative Time [h]")
    fig.supylabel("Magnetic Field [mG]")
    fig.legend(loc='outside upper right')

    # Display plot
    plt.show()


# plot_sensor_data(detail_level='Low') # for testing
