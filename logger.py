"""
Logging functionality for GUI to call (on start button)
"""
import serial
import numpy as np
import time
import csv
import matplotlib.pyplot as plt
from datetime import datetime


# For testing
# class MockSerial:
#     def readline(self):
#         # Generate fake data for testing
#         fake_x = np.random.randint(0, 1201) - 600
#         fake_y = np.random.randint(0, 1201) - 600
#         fake_z = np.random.randint(0, 1201) - 600
#         fake_data = "{},{},{}\n".format(fake_x, fake_y, fake_z)
#         return fake_data.encode()

# def close(self):
#     pass


def get_data(COM_port, stop_event, log_flag, callback=None):
    ser = None
    try:
        # ser = MockSerial() # For testing
        ser = serial.Serial(COM_port, 115200, timeout=1)

        time.sleep(2)
        print(f"Start reading from {COM_port}")

        with open("sensor_data.csv", mode="a", newline="") as file:
            writer = csv.writer(file)
            # Check if file is empty, then write headers
            if file.tell() == 0:
                writer.writerow(["Time", "X", "Y", "Z"])

            # Loop to read and (maybe) log data
            while not stop_event.is_set():
                line = ser.readline()
    
                if line:
                    str_line = line.decode().strip()
                    # print(str_line)
                    # Arduino sends data in the format "x, y, z" in uT
                    # lambda func converts to mG, sensor precision of 6842 LSB/gauss
                    x, y, z = map(
                        lambda val: round(float(val) / 6842 * 1000, 3),
                        str_line.split(","),
                    )
                    if log_flag:
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        writer.writerow([timestamp, x, y, z])
    
                    if callback:
                        callback(x, y, z)
                time.sleep(0.01)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        if ser is not None:
            ser.close()
        print("Serial port closed.")
