''' Quick Serial Port to CSV logger
'''

import serial

#Open port
COM_PORT = 'COM6'

try:
    ser = serial.Serial(COM_PORT, 115200)
    filename = 'quicklog.csv'

    with open(filename, "w") as file:
        file.write('Serial Data\n')

        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').rstrip()  # Read a line and strip newline
                print(line)  # Print to console (optional)
                file.write(f"{line}\n")  
except KeyboardInterrupt:
    print("Interrupted, bailing")
finally:
    ser.close()
    print('Serial port closed.')