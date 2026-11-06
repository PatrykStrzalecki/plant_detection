import customtkinter as ctk

from random import randint

class Plant:
    def __init__(
            self, 
            x : int = 0, 
            y : int = 0, 
            size : int = 40, 
            canvas : ctk.CTkCanvas = None
    ):
        self.x = x
        self.y = y
        self.size = size
        self.canvas = canvas
        
        # Colors for different categories
        self.category_colors = {
            1: '#2ecc71',
            2: '#3498db',
            3: '#e67e22',
            4: '#e74c3c'
        }

        self.category = 0  # Default category (unclassified)
        color = self.category_colors.get(self.category, "#606863")
        self.id = self.canvas.create_oval(x, y, x + size, y + size, fill=color, outline="#000000", width=2, tags="plant")

    def move(self, x_speed : int = 0, y_speed : int = 0):
        self.x += x_speed
        self.y += y_speed
        self.canvas.coords(self.id, self.x, self.y, self.x + self.size, self.y + self.size)

    def set_category(self, category : int = 0) -> int:
        if not category:
            category = randint(1, 4)
        self.category = category

        # Update plant color if canvas already exists
        if hasattr(self, 'id') and self.canvas:
            color = self.category_colors.get(self.category, '#089242')
            self.canvas.itemconfig(self.id, fill=color)
            
        return category