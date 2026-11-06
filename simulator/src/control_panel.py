import customtkinter as ctk

from defaults import PADX, PADY
from typing import Callable

class ControlPanel(ctk.CTkFrame):
    def __init__(
            self, 
            master: ctk.CTk, 
            toggle_simulation : Callable[[], None],
            add_object : Callable[[], None],
            reset_simulation : Callable[[], None],
            **kwargs
    ) -> None:
        super().__init__(master, **kwargs)
        self.configure(fg_color = '#2c3e50', corner_radius = 10)
        self.grid(row = 2, column = 0, sticky = "ew", padx = PADX, pady = (PADY / 2, PADY))
        self.grid_columnconfigure(0, weight = 1)
        self.grid_columnconfigure(1, weight = 1)
        self.grid_columnconfigure(2, weight = 1)
        self.grid_columnconfigure(3, weight = 1)

        self.start_button = ctk.CTkButton(
            self, 
            text = "Start Simulation", 
            command = toggle_simulation,
            font = ('Arial', 14, 'bold'), 
            corner_radius = 8,
            fg_color = '#27ae60', 
            hover_color = '#2ecc71',
            height = 40
        )
        self.start_button.grid(row = 0, column = 0, padx = PADX, pady = PADY, sticky = "ew")
        
        self.reset_button = ctk.CTkButton(
            self, 
            text = "Reset", 
            command = reset_simulation,
            font = ('Arial', 14, 'bold'), 
            corner_radius = 8,
            fg_color = '#e67e22', 
            hover_color = '#f39c12',
            height = 40
        )
        self.reset_button.grid(row = 0, column = 1, padx = PADX, pady = PADY, sticky = "ew")
        
        self.add_object_button = ctk.CTkButton(
            self, 
            text = "Add Object", 
            command = add_object,
            font = ('Arial', 14, 'bold'), 
            corner_radius = 8,
            fg_color = '#3498db', 
            hover_color = '#5dade2',
            height = 40
        )
        self.add_object_button.grid(row = 0, column = 2, padx = PADX, pady = PADY, sticky = "ew")

        self.status_label = ctk.CTkLabel(
            self, 
            text = "Status: Stopped",
            font = ('Arial', 14, 'bold')
        )
        self.status_label.grid(row = 0, column = 3, padx = PADX, pady = PADY, sticky = "ew")
