"""
Reads in sensor_data csv and plots, called from plot button of GUI
"""

import pandas as pd
import matplotlib.pyplot as plt


def plot_sensor_data():
    plt.close()
    # Load data
    data = pd.read_csv("sensor_data.csv")

    # Convert columns to numeric, coercing errors to NaN
    data[["X", "Y", "Z"]] = data[["X", "Y", "Z"]].apply(pd.to_numeric, errors="coerce")

    # Optionally, handle NaN values - e.g., drop them
    data = data.dropna(subset=["X", "Y", "Z"])

    # Generate relative time in seconds given the sample rate
    sample_rate = 80  # Hz
    data["Relative Time"] = data.index * (1 / sample_rate)

    # Plot data
    plt.plot(data["Relative Time"], data["X"], label="X")
    plt.plot(data["Relative Time"], data["Y"], label="Y")
    plt.plot(data["Relative Time"], data["Z"], label="Z")

    # Label axes
    plt.xlabel("Time (s)")
    plt.ylabel("Magnetic Field (mG)")

    # Add title and legend
    plt.title("Magnetic Field vs Time")
    plt.grid()
    plt.legend()
    plt.tight_layout()

    # Display plot
    plt.show()


# plot_sensor_data()
