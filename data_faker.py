"""
Helper script to generate large sets of random sensor data to test plotting functionality
"""

import pandas as pd
import numpy as np


def generate_fake_data(duration):
    # Calculate the number of data points
    sample_rate = 80  # Hz
    num_data_points = int(duration * sample_rate)

    # Generate time intervals
    time_intervals = pd.date_range(
        start="2023-01-01", periods=num_data_points, freq="12.5ms"
    )

    # Generate random X, Y, Z values
    x_values = np.random.randint(-1000, 1001, size=num_data_points)
    y_values = np.random.randint(-1000, 1001, size=num_data_points)
    z_values = np.random.randint(-1000, 1001, size=num_data_points)

    # Create a DataFrame
    df = pd.DataFrame(
        {"Time": time_intervals, "X": x_values, "Y": y_values, "Z": z_values}
    )

    # Save to CSV
    df.to_csv("fake_sensor_data.csv", index=False)
    print(
        f"Generated {num_data_points} data points and saved to 'fake_sensor_data.csv'."
    )


# Example usage
test_duration = 1.7e4
generate_fake_data(duration=test_duration)
