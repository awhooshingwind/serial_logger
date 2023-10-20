"""

Program for monitoring arduino serial magnetometer data 
with option to log to sensor_data.csv and plot from that file

"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import serial.tools.list_ports
from logger import get_data
import plotter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
import numpy as np
from collections import deque


# --- Functions to control logging ---
def stop_logging(stop_event):
    stop_event.set()


# --- GUI Application ---


class App:
    MAX_BUFFER_SIZE = int(2.88e6)  # 1hr of data at 80 Hz sampling rate
    data_buffer = deque(maxlen=MAX_BUFFER_SIZE)

    def close_main_window(self):
        # Close the monitor window if it's open
        if hasattr(self, "monitor_window"):
            self.close_monitor()

        # Stop any running logging threads
        self.stop_event.set()

        # Ensure the logging thread is stopped before moving on
        if hasattr(self, "logging_thread"):
            self.logging_thread.join(timeout=5.0)

        # Destroy the main window
        self.root.destroy()

    def __init__(self, root):
        self.root = root
        self.root.protocol("WM_DELETE_WINDOW", self.close_main_window)
        root.title("Data Logger")

        # Status Label
        self.status_label = tk.Label(root, text="Status: Idle")
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

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

        # Stream Button
        self.stream_button = tk.Button(
            self.button_frame, text="Stream", command=self.start_stream
        )
        self.stream_button.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)

        # Log Button
        self.log_button = tk.Button(
            self.button_frame, text="Log", command=self.start_logging
        )

        self.log_button.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        # Stop Button
        self.stop_button = tk.Button(
            self.button_frame, text="Stop", command=self.stop_logging, state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)

        # Frame for Detail Level and Plot Button
        self.detail_plot_frame = tk.Frame(root)
        self.detail_plot_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # Detail Level Label and Selection within the frame
        self.detail_label = tk.Label(self.detail_plot_frame, text="Detail Level:")
        self.detail_label.pack(side=tk.LEFT, padx=5, pady=5)

        self.detail_levels = ["High", "Medium", "Low"]
        self.detail_selector = ttk.Combobox(
            self.detail_plot_frame,
            values=self.detail_levels,
            state="readonly",
            width=10,
        )
        self.detail_selector.set("Medium")  # default value
        self.detail_selector.pack(side=tk.LEFT, padx=5, pady=5)

        # Plot Button with modified command to pass detail level, packed within the frame
        self.plot_button = tk.Button(
            self.detail_plot_frame,
            text="Plot",
            command=lambda: plotter.plot_sensor_data(self.detail_selector.get()),
        )
        self.plot_button.pack(side=tk.LEFT, fill=tk.X, padx=5, pady=5, expand=True)

        #
        # Monitor Button
        self.monitor_button = tk.Button(
            root, text="Monitor", command=self.launch_monitor
        )
        self.monitor_button.pack(
            side=tk.BOTTOM, padx=35, pady=5, fill=tk.X, expand=True
        )

        # Thread stop event
        self.stop_event = threading.Event()

    def start_logging(self):
        self.start_stream(log_flag=True)
    
    def start_stream(self, log_flag=False):
        selected_port = self.com_port.get()
        # selected_port = "A"  # For testing only
        if not selected_port:
            messagebox.showerror(
                "Error", "Please select a COM port before starting logging."
            )
            return
        self.log_button.config(state=tk.DISABLED)
        self.stream_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text=f"Status: {'Logging' if log_flag else 'Streaming'} on {selected_port}")
        # Reset the stop event
        self.stop_event.clear()
        # Create and start a new logging thread
        self.logging_thread = threading.Thread(
            target=get_data,
            args=(
                selected_port,
                self.stop_event,
                log_flag,
                self.append_to_buffer,
            ),
            daemon=True,
        )
        self.logging_thread.start()

    def append_to_buffer(self, x, y, z):
        # This function will be called by the logger to add data
        App.data_buffer.append((x, y, z))

    def stop_logging(self):
        self.log_button.config(state=tk.NORMAL)
        self.stream_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Idle")
        # Stop the logging thread
        self.stop_event.set()
        # Ensure the logging thread is stopped before moving on
        if hasattr(self, "logging_thread"):
            self.logging_thread.join()

    def launch_monitor(self):
        # Check if the monitor window is already open
        if hasattr(self, "monitor_window"):
            # Close the monitor window
            self.close_monitor()
            return

        # Create new window for monitoring
        self.monitor_window = tk.Toplevel(self.root)
        self.monitor_window.title("Monitor")
        self.monitor_window.geometry("900x650")

        # Frame for the monitor labels
        self.monitor_label_frame = tk.Frame(self.monitor_window)
        self.monitor_label_frame.pack(padx=20, pady=5)

        # Static text labels
        self.static_label_title = tk.Label(
            self.monitor_label_frame,
            text="Lab B Field [mG]",
            font=("Arial", 30),
            fg="black",
        )
        self.static_label_x = tk.Label(
            self.monitor_label_frame,
            text="X:",
            font=("Arial", 40),
            fg="blue",
        )
        self.static_label_y = tk.Label(
            self.monitor_label_frame,
            text="   Y:",
            font=("Arial", 40),
            fg="orange",
        )
        self.static_label_z = tk.Label(
            self.monitor_label_frame,
            text="   Z:",
            font=("Arial", 40),
            fg="green",
        )

        # Dynamic number labels
        self.dynamic_label_x = tk.Label(
            self.monitor_label_frame,
            text="      ",
            font=("Arial", 40),
            fg="blue",
        )
        self.dynamic_label_y = tk.Label(
            self.monitor_label_frame,
            text="      ",
            font=("Arial", 40),
            fg="orange",
        )
        self.dynamic_label_z = tk.Label(
            self.monitor_label_frame,
            text="      ",
            font=("Arial", 40),
            fg="green",
        )

        # Pack the labels in order
        self.static_label_title.pack(side=tk.TOP)
        self.static_label_x.pack(side=tk.LEFT)
        self.dynamic_label_x.pack(side=tk.LEFT)
        self.static_label_y.pack(side=tk.LEFT)
        self.dynamic_label_y.pack(side=tk.LEFT)
        self.static_label_z.pack(side=tk.LEFT)
        self.dynamic_label_z.pack(side=tk.LEFT)

        # Create a Figure and a Canvas to embed the plot in tkinter
        self.fig, self.ax = plt.subplots(figsize=(4, 7))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.monitor_window)

        # Add the navigation toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.monitor_window)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        # Pack the canvas
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        # Create the lines for x, y, and z data with empty lists
        (self.line_x,) = self.ax.plot([], [], label="X", color="blue")
        (self.line_y,) = self.ax.plot([], [], label="Y", color="orange")
        (self.line_z,) = self.ax.plot([], [], label="Z", color="green")

        # Some other plot configurations
        self.ax.legend(loc="upper right")
        self.ax.set_title("B Field Monitor")
        self.ax.set_xlabel("Sample Number")
        self.ax.set_ylabel("Magnetic Field [mG]")
        self.ax.grid(True)

        # Update the monitor label and plot at intervals
        self.update_monitor()
        # Bind the close event of the monitor window to stop the updates
        self.monitor_window.protocol("WM_DELETE_WINDOW", self.close_monitor)

    def update_monitor(self):
        # Check if there's any data to display
        if not self.root:
            return
        if App.data_buffer and hasattr(self, "monitor_window"):
            x, y, z = App.data_buffer[-1]  # Get the latest reading
            # Update the dynamic labels
            self.dynamic_label_x.config(text="{:6.2f}".format(x))
            self.dynamic_label_y.config(text="{:6.2f}".format(y))
            self.dynamic_label_z.config(text="{:6.2f}".format(z))

            # Append the latest data to the plot
            self.line_x.set_xdata(
                np.append(self.line_x.get_xdata(), len(self.line_x.get_xdata()))
            )
            self.line_x.set_ydata(np.append(self.line_x.get_ydata(), x))

            self.line_y.set_xdata(
                np.append(self.line_y.get_xdata(), len(self.line_y.get_xdata()))
            )
            self.line_y.set_ydata(np.append(self.line_y.get_ydata(), y))

            self.line_z.set_xdata(
                np.append(self.line_z.get_xdata(), len(self.line_z.get_xdata()))
            )
            self.line_z.set_ydata(np.append(self.line_z.get_ydata(), z))

            # Automatically adjust the axes limits
            self.ax.relim()
            self.ax.autoscale_view()

            # Redraw the plot
            self.canvas.draw()

            # Check if the monitor window is still available before scheduling the next update
            if hasattr(self, "monitor_window"):
                self.after_id = self.monitor_window.after(600, self.update_monitor)

    def close_monitor(self):
        # Cancel the after updates
        if hasattr(self, "after_id"):
            self.monitor_window.after_cancel(self.after_id)
        # Close the matplotlib figure
        if hasattr(self, "fig"):
            plt.close(self.fig)
        # Destroy the monitor window
        if hasattr(self, "monitor_window"):
            self.monitor_window.destroy()
        # Remove the reference
        if hasattr(self, "monitor_window"):
            delattr(self, "monitor_window")


# --- Main ---
root = tk.Tk()
root.geometry("275x225")
app = App(root)
root.mainloop()
