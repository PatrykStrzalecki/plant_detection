import customtkinter as ctk

from defaults import PADX, PADY, CANVAS_WIDTH, CANVAS_HEIGHT, GRID

class Canvas(ctk.CTkCanvas):
    def __init__(self, master: ctk.CTk, width: int = CANVAS_WIDTH, height: int = CANVAS_HEIGHT):
        super().__init__(master, width = width, height = height, bg = "#34495e", highlightthickness = 0)
        self.grid(row = 1, column = 0, padx = PADX, pady = PADY / 2)
        self.grid_propagate(False)
        self.draw_grid()

    def draw_grid(self) -> None:
        for x in range(0, CANVAS_WIDTH, GRID):
            self.create_line(x, 0, x, CANVAS_HEIGHT, fill = '#7f8c8d', width = 1, dash = (2, 4))

        for y in range(0, CANVAS_HEIGHT, GRID):
            self.create_line(0, y, CANVAS_WIDTH, y, fill = '#7f8c8d', width = 1, dash = (2, 4))

        self.create_text(10, 15, text = "0,0", fill = 'white', font = ('Arial', 10))
        self.create_text(CANVAS_WIDTH - 30, 15, text = f"{CANVAS_WIDTH},0", fill = 'white', font = ('Arial', 10))
        self.create_text(10, CANVAS_HEIGHT - 10, text = f"0,{CANVAS_HEIGHT}", fill = 'white', font = ('Arial', 10))
