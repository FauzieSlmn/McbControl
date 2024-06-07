import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import *
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
import mysql.connector
from datetime import datetime, timedelta
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
from PIL import Image, ImageTk

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("APLIKASI MONITORING")

        self.slave_address = '192.168.1.7'  # IP address slave
        self.port = 2333  # Port Modbus TCP/IP
        self.unit_ids = [1, 2, 3]  # ID slave
        self.geometry("1000x400")  
        
        # Load background image
        self.background_image = Image.open("background_image.jpg")
        self.coil_status = {1: False, 2: False, 3: False}
        # Rotate the image by 90 degrees
        self.resized_image = self.background_image.resize((1000, 400))
        # Convert the rotated image to PhotoImage object
        self.background_photo = ImageTk.PhotoImage(self.resized_image)

        
        # Create a canvas to place widgets on
        self.canvas = tk.Canvas(self, width=1000, height=400)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self.background_photo, anchor="nw")
        
        # Create widgets on canvas
        self.create_widgets()

    def create_widgets(self):
        # Your buttons and other widgets go here
        
        self.button_read_data1 = tk.Button(self.canvas, text="1", command=lambda: self.write_coil_single_unit(1))
        self.button_read_data1.place(x=215, y=70)
        
        self.button_read_data2 = tk.Button(self.canvas, text="2", command=lambda: self.write_coil_single_unit(2))
        self.button_read_data2.place(x=365, y=70)

        self.button_read_data3 = tk.Button(self.canvas, text="3", command=lambda: self.write_coil_single_unit(3))
        self.button_read_data3.place(x=450, y=70)

        self.popup_button = tk.Button(self.canvas, text="$", command=self.open_popup)
        self.popup_button.place(x=215, y=100)

        
        self.button_exit = tk.Button(self.canvas, text="Keluar", command=self.quit)
        self.button_exit.grid(row=3, column=0, columnspan=2, padx=10, pady=5)

    # Other methods of your class...
    def open_popup(self):
        # Function to open the popup window
        popup_window = tk.Toplevel(self)
        popup_window.title("Popup Window")
        popup_window.geometry("800x600")

        # Fetch data from database and create the plot
        data = self.fetch_data_from_database(1)  # Adjust slave_addresses according to your data
        if data:
            fig, ax = plt.subplots()
            ax.plot(data['timestamps'], data['avg_power'], marker='o')
            ax.set_title('Average Power Consumption per Minute')
            ax.set_xlabel('Time')
            ax.set_ylabel('Power (kWh/min)')

            # Create a canvas widget for Matplotlib
            canvas = FigureCanvasTkAgg(fig, master=popup_window)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            # Add a close button to the popup window
            close_button = tk.Button(popup_window, text="Close", command=popup_window.destroy)
            close_button.pack(pady=5)

    def fetch_data_from_database(self, slave_addresses):
        # Simulated data fetching from database
        timestamps = [1, 2, 3, 4, 5,6,7,8,9,10]  # Example timestamps
        avg_power = [10, 12, 10, 14, 15, 14,21,22,26 ,12]  # Example average power values
        data = {'timestamps': timestamps, 'avg_power': avg_power}
        return data

    def write_coil_single_unit(self, value):
        try:
            client = ModbusClient(host=self.slave_address, port=self.port, unit_id=value, auto_open=True)
            client.connect()
            self.coil_status[value] = not self.coil_status[value]
            client.write_coil(1,self.coil_status[value],unit = value)
            self.update_button_color()
            print(f"Successfully wrote value {value} to coil {1} on slave {self.slave_address}, unit ID {value}")
        except Exception as e:
            print(f"Failed to write value to coil: {e}")
        finally:
            client.close()

        # Your method implementation...
    
    def update_button_color(self):
        for value in self.coil_status:
            if self.coil_status[value]:
                if value == 1:
                    self.button_read_data1.config(bg="green")  # Change to green when coil is on
                elif value == 2:
                    self.button_read_data2.config(bg="green")  # Change to green when coil is on
                elif value == 3:
                    self.button_read_data3.config(bg="green")  # Change to green when coil is on
            else:
                if value == 1:
                    self.button_read_data1.config(bg="red")    # Change to red when coil is off
                elif value == 2:
                    self.button_read_data2.config(bg="red")    # Change to red when coil is off
                elif value == 3:
                    self.button_read_data3.config(bg="red")    # Change to red when coil is off


if __name__ == "__main__":
    app = App()
    app.mainloop()

