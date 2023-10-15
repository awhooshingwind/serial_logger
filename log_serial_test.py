"""
Magnetic Field Data logger test script
Log data from LIS3MDL sensor into csv file
"""
import serial
import numpy as np
import time
import csv
import matplotlib.pyplot as plt
from datetime import datetime

# Set up Serial Port Connection
COM = 'COM6'
ser = serial.Serial(COM, 115200, timeout=1)
time.sleep(2)
sample_rate = 80 # Hz (can be changed in Arduino sketch)

# Configure duration/number of samples
duration = 5 #s
# N = 1000
N = int(duration * sample_rate)
data = np.zeros((N,3))

# Open (or create) a CSV file for appending data
with open('sensor_data.csv', mode='a', newline='') as file:
    writer = csv.writer(file)
    # Write header once
    writer.writerow(["Time", "X", "Y", "Z"])
    
    # Loop to read and record data
    for i in range(N):
        line = ser.readline()
        if line:
            str_line = line.decode().strip()
            print(str_line)
            # Arduino sends data in the format "x, y, z"
            x, y, z = map(float, str_line.split(','))
            timestamp = datetime.now().strftime("%m-%d %H:%M:%S")
            writer.writerow([timestamp, x, y, z])

            data[i] = [x,y,z]

# Close the serial port
ser.close()

# Plotting
relative_time = np.arange(0, N)*(1/sample_rate)
# plt.plot(data[:,0])
plt.plot(relative_time, data[:,0], label='X')
plt.plot(relative_time, data[:,1], label='Y')
plt.plot(relative_time, data[:,2], label='Z')
plt.xlabel('Time [s]')
plt.ylabel('Magnetic Field (uTesla)')
# plt.title('Magnetic Field vs. Sampling Time')
plt.grid()
plt.legend()
plt.tight_layout()
plt.show()