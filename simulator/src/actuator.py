import customtkinter as ctk

class Actuator:
    def __init__(
            self, 
            x1 : int, 
            y1 : int, 
            x2 : int, 
            y2 : int,
            color : str = "#55504f", 
            canvas : ctk.CTkCanvas = None
    ):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.color = color
        self.canvas = canvas
        self.is_mounted = False
        self.is_active = False
        self.category = self.set_category()
        self.id = None
        self.offset = -10

    def mount_actuator(self):
        if not self.is_mounted:
            self.id = self.canvas.create_rectangle(
                self.x1, self.y1, self.x2, self.y2, fill = self.color, tags = "actuator"
            )
            self.is_mounted = True
        return self
    
    def unmount_actuator(self):
        if self.is_mounted:
            self.canvas.delete(self.id)
            self.is_mounted = False
    
    def set_category(self, category : int = 0) -> None:
        self.category = category

    def activate(self) -> None:
        if self.is_mounted:
            self.canvas.coords(self.id, self.x1, self.y1  + self.offset, self.x2, self.y2  + self.offset)
            self.change_color(is_active = True)
    
    def deactivate(self) -> None:
        if self.is_mounted:
            self.canvas.coords(self.id, self.x1, self.y1, self.x2, self.y2)
            self.change_color(is_active = False)

    def change_color(self, is_active : bool = False) -> None:
        self.color = "#333131" if is_active else "#55504f"
        if self.is_mounted:
            self.canvas.itemconfig(self.id, fill = self.color)