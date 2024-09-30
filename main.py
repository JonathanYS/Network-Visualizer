"""
This program was written by Yonatan Deri.
It follows the PEP8 guidelines.

Description:
    This file serves as the main file. It relies on the arp_scan.py file.
    This is a simple program for scanning local networks and graphically visualize them.

License:
    This program is under the GNU GPLv3 License.
"""

# GUI related Imports
import customtkinter

# Threading related Imports
import threading

# Miscellaneous Imports
import time
import math
from PIL import Image, ImageTk
import os

# Imports of Self-Made files
import arp_scan

APP_TITLE = "Network Visualizer - written by Yonatan Deri."

ABOUT_FILE = "special_credits"

WIDTH_RATIO = 4.2424242424242424242424242424242
HEIGHT_RATIO = 1.0668151447661469933184855233853

WIDTH = 700
HEIGHT = 479

devices = {}


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title(APP_TITLE)
        self.geometry("700x479")

        customtkinter.set_appearance_mode("Dark")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.resizable(True, True)

        # Images
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "gui_images")
        self.iconbitmap(os.path.join(image_path, "lan.ico"))
        self.host_image = ImageTk.PhotoImage(Image.open(os.path.join(image_path, "host.png")), size=(10, 10))
        self.about_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "info_dark.png")),
                                                  dark_image=Image.open(os.path.join(image_path, "info_light.png")),
                                                  size=(20, 20))
        self.home_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "home_dark.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "home_light.png")),
                                                 size=(20, 20))

        # Create Home frame
        self.home_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")

        # create navigation frame
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0, width=int(WIDTH / WIDTH_RATIO),
                                                       height=int(HEIGHT / HEIGHT_RATIO))

        self.navigation_frame.grid(row=0, column=0, sticky="nsew")

        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text="  Network Visualizer  ",
                                                             compound="left",
                                                             font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        # Create Home button
        self.home_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10,
                                                   text="Home",
                                                   fg_color="transparent", text_color=("gray10", "gray90"),
                                                   hover_color=("gray70", "gray30"), image=self.home_image,
                                                   anchor="w",
                                                   command=self.home_button_event)
        self.home_button.grid(row=1, column=0, sticky="ew")

        # Create commands Frame
        self.commands_frame = customtkinter.CTkFrame(self.home_frame, corner_radius=0, fg_color="transparent",
                                                     border_width=2, border_color="black")
        self.commands_frame.pack(side=customtkinter.BOTTOM, pady=10, fill="x")
        self.commands_frame.pack_propagate(False)
        self.commands_frame.configure(width=400, height=100)

        # Create Display Network button
        self.display_network_button = customtkinter.CTkButton(self.commands_frame,
                                                              border_spacing=10,
                                                              text="Display Network",
                                                              fg_color="green", text_color=("gray10", "gray90"),
                                                              hover_color=("gray70", "gray30"),
                                                              command=self.list_subnets_thread)
        self.display_network_button.pack(pady=20)

        self.canvas = customtkinter.CTkCanvas(self.home_frame, bg="#242424", highlightthickness=0)

        # create CTk scrollbars for the canvas (horizontal and vertical)
        canvas_scrollbar_x = customtkinter.CTkScrollbar(self.canvas, orientation="horizontal",
                                                        command=self.canvas.xview)
        canvas_scrollbar_x.pack(side='bottom', fill='x')
        canvas_scrollbar_y = customtkinter.CTkScrollbar(self.canvas, command=self.canvas.yview)
        canvas_scrollbar_y.pack(side="right", fill='y')
        self.canvas.configure(xscrollcommand=canvas_scrollbar_x.set)
        self.canvas.configure(yscrollcommand=canvas_scrollbar_y.set)

        # Create About button
        self.about_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40,
                                                    border_spacing=10, text="About",
                                                    fg_color="transparent", text_color=("gray10", "gray90"),
                                                    hover_color=("gray70", "gray30"), image=self.about_image,
                                                    anchor="w", command=self.about_button_event)
        self.about_button.grid(row=7, column=0, sticky="ew")

        # Create the subnets panel
        self.subnets_frame = customtkinter.CTkScrollableFrame(self.home_frame, corner_radius=0)
        self.subnets_frame.pack(side=customtkinter.TOP, fill="both", expand=True)

        # Create verbose text box for scanning details
        self.scanning_details = customtkinter.CTkTextbox(self.home_frame,
                                                         fg_color="transparent", border_width=2,
                                                         border_color="black")
        self.scanning_details.pack(side=customtkinter.BOTTOM, fill="both", expand=True)
        self.scanning_details.configure(state="disabled")

        # Create appearance mode menu
        self.appearance_mode_menu = customtkinter.CTkOptionMenu(self.navigation_frame,
                                                                values=["Dark", "Light", "System"],
                                                                command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=8, column=0, padx=20, pady=20, sticky="s")

        # Create about frame
        about_file_text = self.about_text_pull()
        self.about_frame = customtkinter.CTkScrollableFrame(self, corner_radius=0, fg_color="transparent")
        self.about_label = customtkinter.CTkLabel(self.about_frame, text=about_file_text, justify="left")
        self.about_label.grid(row=0, column=0)

        # Start the GUI in the Home frame
        self.select_frame_by_name("home")

    @staticmethod
    def about_text_pull() -> str:
        """
        This function reads the entire about text file and returns it to the gui to display on
        the scrollableFrame (about frame).
        :return str:
        """
        try:
            with open(ABOUT_FILE, 'r') as file:
                contents = file.read()
            return contents
        except (Exception,):
            print("Please put the special_credits file in the used directory of the project.")

    def about_button_event(self) -> None:
        """
        This function gives the parameter "about" as the name of the frame to switch to
        (if the user selected the About button).
        :return None:
        """
        self.select_frame_by_name("about")

    def update_scrollregion(self) -> None:
        # Update the scrollregion based on all items on the canvas
        bbox = self.canvas.bbox("all")
        if bbox:
            extended_bbox = (bbox[0], bbox[1], bbox[2] + 30, bbox[3] + 30)
            self.canvas.configure(scrollregion=extended_bbox)

    def list_subnets_thread(self) -> None:
        """
        Starts the process of listing all subnets in the network as buttons, with their active device counter.
        Needed for the application to keep running regularly.
        :return None:
        """
        threading.Thread(target=self.list_subnets, daemon=True).start()

    def list_subnets(self) -> None:
        """
        Lists all subnets in the network as buttons, with their active device counter.
        :return None:
        """
        global devices
        start_time = time.time()
        self.delete_all_buttons(self.subnets_frame)
        networks = arp_scan.get_active_networks()
        displayed_text = ""
        for network in networks:
            devices[network] = []
            device_counter = 0
            displayed_text += f"Scanning network: {network}\n"
            self.update_textbox(displayed_text)
            clients = arp_scan.scan(network)
            displayed_text += "[*] IP Address      MAC Address\n"
            self.update_textbox(displayed_text)
            for sent, received in clients:
                device_counter += 1
                ip = received.psrc  # Source IP
                mac = received.hwsrc  # Source MAC
                devices[network].append((ip, mac))
                displayed_text += f"{ip}      {mac}\n"
                self.update_textbox(displayed_text)
            self.create_subnet_button(network, device_counter)
        displayed_text += f"\n*****************************\nDone Scanning The Network!\nScanning Time: " \
                          f"{round(time.time() - start_time, 2)} seconds\n*****************************\n"
        self.update_textbox(displayed_text)

    @staticmethod
    def delete_all_buttons(widget) -> None:
        """
        Deletes all buttons inside a given widget.
        :param widget: given widget, from where the buttons will be deleted.
        :return None:
        """
        for widget in widget.winfo_children():
            widget.destroy()

    def update_textbox(self, text: str) -> None:
        """
        Updates the textbox responsible for displaying scanning details, with the given text parameter.
        :param text: updated text for the textbox for displaying scanning details.
        :return None:
        """
        self.scanning_details.configure(state="normal")
        self.scanning_details.delete('0.0', 'end')
        self.scanning_details.insert('0.0', text=text)
        self.scanning_details.configure(state="disabled")
        self.scanning_details.yview_moveto(1)
        self.scanning_details.update_idletasks()  # Ensures the GUI updates immediately

    def create_subnet_button(self, subnet: str, devices_count: int) -> None:
        """
        Create subnet button inside the list of subnet buttons.
        :param subnet: for which the button will be created.
        :param devices_count: indicating the number of devices within the given subnet, within the button details.
        :return: None
        """
        customtkinter.CTkButton(self.subnets_frame, fg_color="#44475a",
                                text=f"Network: {subnet}, Devices: {devices_count}", anchor="w", command=lambda: self.
                                switch2subnet_overview(subnet)).pack(side=customtkinter.TOP, fill="both", expand=True)

    def switch2subnet_overview(self, subnet: str) -> None:
        """
        Switches to the graphical overview of the specified subnet and its devices.

        This function clears the current canvas, hides home widgets, and
        then displays the devices associated with the provided subnet in a
        graphical format. It also establishes bidirectional connections
        between devices (graphically).

        :param subnet: The identifier of the subnet to visualize.
        :return: None
        """
        global devices
        self.clear_canvas()
        self.home_widgets_forget()
        self.canvas.pack(side=customtkinter.TOP, fill="both", expand=True)
        device_positions = {}
        radius = 33  # Radius of the nodes
        nodes_per_row = 3  # Number of nodes per row

        self.arrange_devices_in_rows(subnet, nodes_per_row, device_positions)

        for i in range(len(devices[subnet])):
            for j in range(i + 1, len(devices[subnet])):
                self.draw_bidirectional_connection(devices[subnet][i][0], devices[subnet][j][0],
                                                   device_positions, radius)

        self.arrange_devices_in_rows(subnet, nodes_per_row, device_positions)

    def arrange_devices_in_rows(self, subnet: str, nodes_per_row: int, device_positions: dict) -> None:
        """
        Arranges the active devices within the specified subnet in rows.

        This function positions each device based on the number of nodes
        that should be displayed per row.

        :param subnet: The identifier of the subnet containing devices.
        :param nodes_per_row: The maximum number of devices to display in one row.
        :param device_positions: A dictionary to store the positions of devices.
        :return: None
        """
        for i, device in enumerate(devices[subnet]):
            x = 100 + (i % nodes_per_row) * 200  # Position nodes horizontally
            y = 100 + (i // nodes_per_row) * 200  # Position nodes vertically
            device_positions[device[0]] = (x, y)  # Store center position
            self.canvas.create_image(x, y, image=self.host_image)
            self.canvas.create_text(x, y + 45, text=f"    {device[0]}\n    {device[1]}", fill="white",
                                    font=("TimesNewRoman", 8))

    def draw_bidirectional_connection(self, ip1: str, ip2: str, device_positions: dict, radius: float) -> None:
        """
        Draws a bidirectional connection between two devices.

        This function calculates the positions of the two devices and draws
        a line to represent their connection.

        :param ip1: The IP address of the first device.
        :param ip2: The IP address of the second device.
        :param device_positions: A dictionary containing the positions of devices.
        :param radius: The radius used to offset the connection lines.
        :return: None
        """
        x1, y1 = device_positions[ip1]
        x2, y2 = device_positions[ip2]

        # Draw the connection lines
        self.draw_line(x1, y1, x2, y2, radius)

    def draw_line(self, x1: float, y1: float, x2: float, y2: float, radius: float) -> None:
        """
        Draws a line between two points, offsetting by the specified radius.

        The line is drawn from the edge of the first device to the edge of
        the second device, with an arrow indicating direction.

        :param x1: The x-coordinate of the first device.
        :param y1: The y-coordinate of the first device.
        :param x2: The x-coordinate of the second device.
        :param y2: The y-coordinate of the second device.
        :param radius: The radius of the devices, used to calculate line start/end points.
        :return: None
        """
        angle = math.atan2(y2 - y1, x2 - x1)
        # Move to the edge of the first object
        start_x = x1 + radius * math.cos(angle)
        start_y = y1 + radius * math.sin(angle)

        # Move to the edge of the second object
        end_x = x2 - radius * math.cos(angle)
        end_y = y2 - radius * math.sin(angle)

        # Draw the first direction (A to B)
        self.canvas.create_line(start_x, start_y, end_x, end_y, fill="#44475a", arrow="last")

        # Draw the second direction (B to A)
        self.canvas.create_line(end_x, end_y, start_x, start_y, fill="#44475a", arrow="last")

    def select_frame_by_name(self, name: str) -> None:
        """
        This function is responsible for the "menu" functionality of the gui, the activity of selecting frames
        (and switching them) by getting their name as a parameter.
        :param name:
        :return None:
        """
        # set button color for selected button
        self.home_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")

        # show selected frame
        if name == "home":
            self.home_frame.grid(row=0, column=1, sticky="nsew")

            self.canvas.pack_forget()
            self.home_widgets_restore()
        else:
            self.home_frame.grid_forget()
        if name == "about":
            self.about_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.about_frame.grid_forget()

    def home_button_event(self) -> None:
        """
        This function gives the argument "home" as the name of the frame to switch to
        (if the user selected the home button).
        :return None:
        """
        self.select_frame_by_name("home")

    def home_widgets_forget(self) -> None:
        self.subnets_frame.pack_forget()
        self.scanning_details.pack_forget()
        self.commands_frame.pack_forget()

    def home_widgets_restore(self) -> None:
        self.subnets_frame.pack(side=customtkinter.TOP, fill="both", expand=True)
        self.commands_frame.pack(side=customtkinter.BOTTOM, pady=10, fill="x")
        self.commands_frame.pack_propagate(False)
        self.commands_frame.configure(width=400, height=100)
        self.scanning_details.pack(side=customtkinter.BOTTOM, fill="both", expand=True)
        self.scanning_details.configure(state="disabled")

    def clear_canvas(self) -> None:
        self.canvas.delete("all")
        self.update_scrollregion()

    @staticmethod
    def change_appearance_mode_event(new_appearance_mode: str) -> None:
        """
        This function is responsible for changing the gui appearance mode.
        :param new_appearance_mode:
        :return None:
        """
        customtkinter.set_appearance_mode(new_appearance_mode)


def main() -> None:
    """
    Entry point of the application.

    This function initializes the main application window and starts the
    event loop, allowing the application to run and respond to user
    interactions.

    :return: None
    """
    app = App()
    app.mainloop()


if __name__ == '__main__':
    main()
