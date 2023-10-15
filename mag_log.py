"""
Simple GUI for starting/stopping arduino serial magnetometer data logging
with option for plotting from generated csv
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import serial.tools.list_ports
from logger import log_data
import plotter


# --- Functions to control logging ---
def stop_logging(stop_event):
    stop_event.set()


# --- GUI Application ---


class App:
    def __init__(self, root):
        self.root = root
        root.title("Data Logger")

        # Frame for COM port selection
        self.com_frame = tk.Frame(root)
        self.com_frame.pack(fill=tk.X, padx=5, pady=5)

        # COM Port Selection
        self.com_label = tk.Label(self.com_frame, text="Select COM Port:")
        self.com_label.pack(side=tk.LEFT, padx=5, pady=5)

        self.com_ports = [port.device for port in serial.tools.list_ports.comports()]
        self.com_port = ttk.Combobox(self.com_frame, values=self.com_ports)
        self.com_port.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)

        # Frame for buttons
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(fill=tk.X, padx=5, pady=5)

        # Start Button
        self.start_button = tk.Button(
            self.button_frame, text="Start", command=self.start_logging
        )
        self.start_button.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)

        # Stop Button
        self.stop_button = tk.Button(
            self.button_frame, text="Stop", command=self.stop_logging, state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)

        # Plot Button
        self.plot_button = tk.Button(
            root, text="Plot", command=plotter.plot_sensor_data
        )
        self.plot_button.pack(side=tk.BOTTOM, padx=5, pady=5)

        # Thread stop event
        self.stop_event = threading.Event()

         # Status Label
        self.status_label = tk.Label(root, text="Status: Idle")
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

    def start_logging(self):
        selected_port = self.com_port.get()
        if not selected_port:
            messagebox.showerror("Error", "Please select a COM port before starting logging.")
            return
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text=f"Status: Logging on {selected_port}")
        # Reset the stop event
        self.stop_event.clear()
        # Create and start a new logging thread
        self.logging_thread = threading.Thread(
            target=log_data, args=(selected_port, self.stop_event), daemon=True
        )
        self.logging_thread.start()
    def stop_logging(self):
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Idle")
        # Stop the logging thread
        stop_logging(self.stop_event)

# --- Main ---
root = tk.Tk()
root.geometry("260x150")  # Adjusted for added status label
app = App(root)
root.mainloop()