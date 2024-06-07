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
from ttkthemes import ThemedTk
import my_functions


LARGEFONT = ("Verdana", 25)

class tkinterApp(tk.Tk):
    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry("800x445")
        self.title("APLIKASI MONITORING") 


        # Load background images

        self.background_image_page1 = Image.open("background.png")
        self.resized_image1 = self.background_image_page1.resize((800, 400))
        self.background_photo_page1 = ImageTk.PhotoImage(self.resized_image1)

        self.background_image_page2 = Image.open("background_LT2.png")
        self.resized_image2 = self.background_image_page2.resize((800, 400))
        self.background_photo_page2 = ImageTk.PhotoImage(self.resized_image2)

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (Page1, Page2):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(Page1)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
        


class Page1(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg="light blue")
        self.controller = controller  # Simpan instance controller

        # Create a Canvas to display the background image
        self.canvas = tk.Canvas(self, width=800,height=400)
        self.canvas.pack(fill="both", expand=True)

        # Load the background image
        self.background_image = controller.background_photo_page1
        self.canvas.create_image(0, 0, anchor="nw", image=self.background_image)

        label_text = ttk.Label(self, text="Lantai 1", font=LARGEFONT)
        
        label_text.place(x=0, y=173)


        self.coil_status = {1: False, 2: False, 3: False}
        self.lock_status = {1: False, 2: False, 3: False}

        self.slave_address = '192.168.1.7'  # IP address slave
        self.port = 2333  # Port Modbus TCP/IP
        self.unit_ids = [1, 2, 3]  # ID slave

        self.create_widgets()  # Panggil method create_widgets

    def create_widgets(self):
        # Your widget creation code here

        # Your buttons and other widgets go here
        self.button_read_data1 = tk.Button(self.canvas, text="⇋", command=lambda: self.write_coil_switch(1), width=3, height=1)
        self.button_read_data1.place(x=325, y=100)

        self.button_read_data2 = tk.Button(self.canvas, text="⇋", command=lambda: self.write_coil_switch(2), width=3, height=1)
        self.button_read_data2.place(x=420, y=100)

        self.button_read_data3 = tk.Button(self.canvas, text="⇋", command=lambda: self.write_coil_switch(3), width=3, height=1)
        self.button_read_data3.place(x=610, y=100)

        self.popup_button = tk.Button(self.canvas, text="≈", command=lambda: self.statistic(1))
        self.popup_button.place(x=360, y=100)

        self.popup_button2 = tk.Button(self.canvas, text="≈", command=lambda: self.statistic(2))
        self.popup_button2.place(x=455, y=100)

        self.popup_button3 = tk.Button(self.canvas, text="≈", command=lambda: self.statistic(3))
        self.popup_button3.place(x=645, y=100)

        self.lock_button = tk.Button(self.canvas, text="⇎", command=lambda: self.write_coil_lock(1), width=3, height=1)
        self.lock_button.place(x=380, y=100)
        self.lock_button2 = tk.Button(self.canvas, text="⇎", command=lambda: self.write_coil_lock(2), width=3, height=1)
        self.lock_button2.place(x=476, y=100)
        self.lock_button3 = tk.Button(self.canvas, text="⇎", command=lambda: self.write_coil_lock(3), width=3, height=1)
        self.lock_button3.place(x=667, y=100)


        button1 = ttk.Button(self, text="Page 2", command=lambda: self.controller.show_frame(Page2))
        button1.pack(pady=10)

    # Metode lainnya

    def statistic(self, slave_id):
        # Function to open the popup window
        popup_window = tk.Toplevel(self)
        popup_window.title("Popup Window")
        popup_window.geometry("1000x600")
        result = my_functions.add_numbers(1,1)
        print(result)
        

        # Fetch data from database and create the plot
        data = self.fetch_data_from_database(slave_id)  # Adjust slave_addresses according to your data
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
        try:
        # Buat koneksi ke database
            db_connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="dbsewa"
            )

            if db_connection.is_connected():
                print("Koneksi ke database berhasil!")

            # Buat kursor untuk mengeksekusi kueri SQL
                db_cursor = db_connection.cursor()

            # Eksekusi kueri SQL untuk mengambil data
                query = "SELECT menit, daya FROM avg_menit WHERE slave_id = %s ORDER BY menit"
                db_cursor.execute(query, (slave_addresses,))
                result = db_cursor.fetchall()

            # Buat dictionary untuk menyimpan data hasil query
                data = {'timestamps': [], 'avg_power': []}
                for row in result:
                    data['timestamps'].append(row[0])
                    data['avg_power'].append(row[1])

            # Tutup kursor dan koneksi database
                db_cursor.close()
                db_connection.close()

                return data

        except mysql.connector.Error as error:
            print("Gagal terhubung ke database:", error)

    # Return None jika terjadi kesalahan saat mengambil data
        return None


    def write_coil_switch(self, value):
        client = None  # Inisialisasi variabel client dengan None
        try:
            client = ModbusClient(host=self.slave_address, port=self.port, unit_id=value, auto_open=True)
            client.connect()
            self.coil_status[value] = not self.coil_status[value]
            client.write_coil(1, self.coil_status[value], unit=value)
            self.update_button_color()
            print(f"Successfully wrote value {value} to coil {1} on slave {self.slave_address}, unit ID {value}")
        except Exception as e:
            print(f"Failed to write value to coil: {e}")
        finally:
            if client is not None:  # Pastikan client tidak None sebelum mencoba untuk menutup koneksi
                client.close()


    def write_coil_lock(self, value):
        client = None  # Inisialisasi variabel client dengan None
        try:
            client = ModbusClient(host=self.slave_address, port=self.port, unit_id=value, auto_open=True)
            client.connect()
            self.lock_status[value] = not self.lock_status[value]
            client.write_coil(2, self.lock_status[value], unit=value)
            self.update_button_color()
            print(f"Successfully wrote value {value} to coil {2} on slave {self.slave_address}, unit ID {value}")
        except Exception as e:
            print(f"Failed to write value to coil: {e}")
        finally:
            if client is not None:  # Pastikan client tidak None sebelum mencoba untuk menutup koneksi
                client.close()

    
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
        for value in self.lock_status:
            if self.lock_status[value]:
                if value == 1:
                    self.lock_button.config(bg="green")  # Change to green when coil is on
                elif value == 2:
                    self.lock_button2.config(bg="green")  # Change to green when coil is on
                elif value == 3:
                    self.lock_button3.config(bg="green")  # Change to green when coil is on
            else:
                if value == 1:
                    self.lock_button.config(bg="red")    # Change to red when coil is off
                elif value == 2:
                    self.lock_button2.config(bg="red")    # Change to red when coil is off
                elif value == 3:
                    self.lock_button3.config(bg="red")    # Change to red when coil is off


class Page2(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller  # Simpan instance controller

        # Create a Canvas to display the background image
        self.canvas = tk.Canvas(self, width=1000, height=400)
        self.canvas.pack(fill="both", expand=True)
        self.configure(bg="light blue")


        # Load the background image
        self.background_image = controller.background_photo_page2
        self.canvas.create_image(0, 0, anchor="nw", image=self.background_image)

        label_text = ttk.Label(self, text="Lantai 2", font=LARGEFONT)
        label_text.place(x=0, y=173)
        


        self.coil_status = {1: False, 2: False, 3: False}
        self.lock_status = {1: False, 2: False, 3: False}


        self.slave_address = '192.168.1.7'  # IP address slave
        self.port = 2333  # Port Modbus TCP/IP
        self.unit_ids = [1, 2, 3]  # ID slave

        self.create_widgets()  # Panggil method create_widgets

    def create_widgets(self):
        # Your widget creation code here

        # Your buttons and other widgets go here
        self.button_read_data1 = tk.Button(self.canvas, text="⇋", command=lambda: self.write_coil_switch(1), width=3, height=1)
        self.button_read_data1.place(x=275, y=95)

        self.button_read_data2 = tk.Button(self.canvas, text="⇋", command=lambda: self.write_coil_switch(2), width=3, height=1)
        self.button_read_data2.place(x=422, y=95)

        self.button_read_data3 = tk.Button(self.canvas, text="⇋", command=lambda: self.write_coil_switch(3),width=3, height=1)
        self.button_read_data3.place(x=613, y=95)

        
        

        self.statistic_button = tk.Button(self.canvas, text="≈", command=lambda: self.statistic(1), width=3, height=1)
        self.statistic_button.place(x=310, y=95)

        self.statistic_button2 = tk.Button(self.canvas, text="≈", command=lambda: self.statistic(2))
        self.statistic_button2.place(x=456, y=95)

        self.statistic_button3 = tk.Button(self.canvas, text="≈", command=lambda: self.statistic(3))
        self.statistic_button3.place(x=647, y=95)


        self.lock_button = tk.Button(self.canvas, text="⇎", command=lambda: self.write_coil_lock(1), width=3, height=1)
        self.lock_button.place(x=345, y=95)
        self.lock_button2 = tk.Button(self.canvas, text="⇎", command=lambda: self.write_coil_lock(2), width=3, height=1)
        self.lock_button2.place(x=477, y=95)
        self.lock_button3 = tk.Button(self.canvas, text="⇎", command=lambda: self.write_coil_lock(3), width=3, height=1)
        self.lock_button3.place(x=668, y=95)


        button1 = ttk.Button(self, text="Page 1", command=lambda: self.controller.show_frame(Page1))
        button1.pack(pady=10)

    # Metode lainnya

    def statistic(self, slave_id):
        # Function to open the popup window
        popup_window = tk.Toplevel(self)
        popup_window.title("Popup Window")
        popup_window.geometry("1000x600")

        # Fetch data from database and create the plot
        data = self.fetch_data_from_database(slave_id)  # Adjust slave_addresses according to your data
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
        try:
        # Buat koneksi ke database
            db_connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="dbsewa"
            )

            if db_connection.is_connected():
                print("Koneksi ke database berhasil!")

            # Buat kursor untuk mengeksekusi kueri SQL
                db_cursor = db_connection.cursor()

            # Eksekusi kueri SQL untuk mengambil data
                query = "SELECT menit, daya FROM avg_menit WHERE slave_id = %s ORDER BY menit"
                db_cursor.execute(query, (slave_addresses,))
                result = db_cursor.fetchall()

            # Buat dictionary untuk menyimpan data hasil query
                data = {'timestamps': [], 'avg_power': []}
                for row in result:
                    data['timestamps'].append(row[0])
                    data['avg_power'].append(row[1])

            # Tutup kursor dan koneksi database
                db_cursor.close()
                db_connection.close()

                return data

        except mysql.connector.Error as error:
            print("Gagal terhubung ke database:", error)

    # Return None jika terjadi kesalahan saat mengambil data
        return None


    def write_coil_switch(self, value):
        client = None  # Inisialisasi variabel client dengan None
        try:
            client = ModbusClient(host=self.slave_address, port=self.port, unit_id=value, auto_open=True)
            client.connect()
            self.coil_status[value] = not self.coil_status[value]
            client.write_coil(1, self.coil_status[value], unit=value)
            self.update_button_color()
            print(f"Successfully wrote value {value} to coil {1} on slave {self.slave_address}, unit ID {value}")
        except Exception as e:
            print(f"Failed to write value to coil: {e}")
        finally:
            if client is not None:  # Pastikan client tidak None sebelum mencoba untuk menutup koneksi
                client.close()
        
    def write_coil_lock(self, value):
        client = None  # Inisialisasi variabel client dengan None
        try:
            client = ModbusClient(host=self.slave_address, port=self.port, unit_id=value, auto_open=True)
            client.connect()
            self.lock_status[value] = not self.lock_status[value]
            client.write_coil(2, self.lock_status[value], unit=value)
            self.update_button_color()
            print(f"Successfully wrote value {value} to coil {2} on slave {self.slave_address}, unit ID {value}")
        except Exception as e:
            print(f"Failed to write value to coil: {e}")
        finally:
            if client is not None:  # Pastikan client tidak None sebelum mencoba untuk menutup koneksi
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
        for value in self.lock_status:
            if self.lock_status[value]:
                if value == 1:
                    self.lock_button.config(bg="green")  # Change to green when coil is on
                elif value == 2:
                    self.lock_button2.config(bg="green")  # Change to green when coil is on
                elif value == 3:
                    self.lock_button3.config(bg="green")  # Change to green when coil is on
            else:
                if value == 1:
                    self.lock_button.config(bg="red")    # Change to red when coil is off
                elif value == 2:
                    self.lock_button2.config(bg="red")    # Change to red when coil is off
                elif value == 3:
                    self.lock_button3.config(bg="red")    # Change to red when coil is off
    

        

# Driver Code
app = tkinterApp()
app.mainloop()
