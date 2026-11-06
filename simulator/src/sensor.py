import customtkinter as ctk

from typing import Union

from plant import Plant

class Sensor:
    def __init__(
            self, 
            x1 : int, 
            y1 : int, 
            x2 : int, 
            y2 : int, 
            canvas : ctk.CTkCanvas = None, 
            color : str = "#db380f"
    ):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.color = color
        self.canvas = canvas
        self.is_mounted = False
        self.category = self.set_category()
        self.is_active = False
        self.id = None

    def mount_sensor(self):
        if not self.is_mounted:
            self.id = self.canvas.create_line(
                self.x1, self.y1, self.x2, self.y2, fill = self.color, width = 2, dash = (4, 2), tags = "sensor"
            )
            self.is_mounted = True
        return self

    def unmount_sensor(self):
        if self.is_mounted:
            self.canvas.delete(self.id)
            self.is_mounted = False
    
    def set_category(self, category : int = 0) -> None:
        self.category = category

    def is_active_sensor(self, plants : list[Plant] = None) -> Union[Plant, None]:
        if self.is_mounted:    
            for plant in plants:
                p_x1 = plant.x
                p_x2 = plant.x + plant.size
                p_y1 = plant.y
                p_y2 = plant.y + plant.size
                if (p_x1 <= self.x1 <= p_x2 or p_x1 <= self.x2 <= p_x2):
                    self.is_active = True
                    self.change_color(is_active = self.is_active)
                    return plant
        self.is_active = False
        self.change_color(is_active = self.is_active)
        return None

    def change_color(self, is_active : bool = False) -> None:
        self.color = "#27ae60" if is_active else "#db380f"
        if self.is_mounted:
            self.canvas.itemconfig(self.id, fill = self.color)