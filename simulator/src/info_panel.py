import customtkinter as ctk

from defaults import INFO_PANEL_HEIGHT, PADX, PADY

class InfoPanel(ctk.CTkFrame):
    def __init__(self, master: ctk.CTk, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.configure(fg_color = '#2c3e50', corner_radius = 10, height = INFO_PANEL_HEIGHT)
        self.grid(row = 0, column = 0, sticky = "ew", padx = PADX, pady = (PADY, PADY / 2))
        self.grid_propagate(False)

        for i in range(5):
            self.grid_columnconfigure(i, weight = 1)

        self.belt_speed = 2.0
        self.category_1_count = 0
        self.category_2_count = 0
        self.category_3_count = 0
        self.category_4_count = 0
        
        self.category_colors = {
            1: '#2ecc71',
            2: '#3498db',
            3: '#e67e22',
            4: '#e74c3c'
        }

        self.speed_label = ctk.CTkLabel(
            self, 
            text = f"Speed: {self.belt_speed} px/s",
            font = ('Arial', 12, 'bold'),
            text_color = '#ecf0f1'
        )
        self.speed_label.grid(row = 0, column = 0, padx = PADX, pady = PADY)

        self.category_1_label = ctk.CTkLabel(
            self, 
            text = f"Cat 1: {self.category_1_count}",
            font = ('Arial', 12, 'bold'),
            text_color = self.category_colors[1]
        )
        self.category_1_label.grid(row = 0, column = 4, padx = PADX, pady = PADY)
        
        self.category_2_label = ctk.CTkLabel(
            self, 
            text = f"Cat 2: {self.category_2_count}",
            font = ('Arial', 12, 'bold'),
            text_color = self.category_colors[2]
        )
        self.category_2_label.grid(row = 0, column = 3, padx = PADX, pady = PADY)
        
        self.category_3_label = ctk.CTkLabel(
            self,
            text = f"Cat 3: {self.category_3_count}",
            font = ('Arial', 12, 'bold'),
            text_color = self.category_colors[3]
        )
        self.category_3_label.grid(row = 0, column = 2, padx = PADX, pady = PADY)
        
        self.category_4_label = ctk.CTkLabel(
            self, 
            text = f"Cat 4: {self.category_4_count}",
            font = ('Arial', 12, 'bold'),
            text_color = self.category_colors[4]
        )
        self.category_4_label.grid(row = 0, column = 1, padx = PADX, pady = PADY)
    
    def update_belt_speed(self, speed: float) -> None:
        self.belt_speed = speed
        self.speed_label.configure(text=f"Speed: {self.belt_speed:.1f} px/s")
    
    def increment_category(self, category: int) -> None:
        if category == 1:
            self.category_1_count += 1
            self.category_1_label.configure(text=f"Cat 1: {self.category_1_count}")
        elif category == 2:
            self.category_2_count += 1
            self.category_2_label.configure(text=f"Cat 2: {self.category_2_count}")
        elif category == 3:
            self.category_3_count += 1
            self.category_3_label.configure(text=f"Cat 3: {self.category_3_count}")
        elif category == 4:
            self.category_4_count += 1
            self.category_4_label.configure(text=f"Cat 4: {self.category_4_count}")
    
    def decrement_category(self, category: int) -> None:
        if category == 1 and self.category_1_count > 0:
            self.category_1_count -= 1
            self.category_1_label.configure(text=f"Cat 1: {self.category_1_count}")
        elif category == 2 and self.category_2_count > 0:
            self.category_2_count -= 1
            self.category_2_label.configure(text=f"Cat 2: {self.category_2_count}")
        elif category == 3 and self.category_3_count > 0:
            self.category_3_count -= 1
            self.category_3_label.configure(text=f"Cat 3: {self.category_3_count}")
        elif category == 4 and self.category_4_count > 0:
            self.category_4_count -= 1
            self.category_4_label.configure(text=f"Cat 4: {self.category_4_count}")
    
    def reset_counters(self) -> None:
        self.category_1_count = 0
        self.category_2_count = 0
        self.category_3_count = 0
        self.category_4_count = 0
        self.category_1_label.configure(text=f"Cat 1: {self.category_1_count}")
        self.category_2_label.configure(text=f"Cat 2: {self.category_2_count}")
        self.category_3_label.configure(text=f"Cat 3: {self.category_3_count}")
        self.category_4_label.configure(text=f"Cat 4: {self.category_4_count}")
    
    def get_category_count(self, category: int) -> int:
        if category == 1:
            return self.category_1_count
        elif category == 2:
            return self.category_2_count
        elif category == 3:
            return self.category_3_count
        elif category == 4:
            return self.category_4_count
        return 0
    
    def get_total_plants(self) -> int:
        return self.category_1_count + self.category_2_count + self.category_3_count + self.category_4_count