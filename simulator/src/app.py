import customtkinter as ctk
import asyncio
import threading
from belt import Belt
from plant import Plant
from sensor import Sensor
from info_panel import InfoPanel
from control_panel import ControlPanel
from canvas import Canvas
from actuator import Actuator
from pathlib import Path
from redis_client import SimulatorRedisClient
from defaults import GRID, CANVAS_WIDTH, IMAGES_FOLDER

class App(ctk.CTk):

    def __init__(self, fg_color = None, **kwargs):
        super().__init__(fg_color, **kwargs)
        self.redis_client = SimulatorRedisClient()
        
        self.redis_thread = None
        self.start_redis_listener()
        
        self.title("Sorting Simulator")
        #self.resizable(False, False)
        self.grid_rowconfigure(0, weight = 0)
        self.grid_rowconfigure(1, weight = 0)
        self.grid_rowconfigure(2, weight = 0)
        self.grid_columnconfigure(0, weight = 1)
        self.info_panel = InfoPanel(self)
        self.canvas = Canvas(self)
        self.control_panel = ControlPanel(
            self,
            toggle_simulation = self.toggle_simulation,
            add_object = self.add_object,
            reset_simulation = self.reset_simulation
        )
        self.draw_layout()
        self.is_running : bool = False
        self.plant_cnt = 0
        self.belt_movement_status_id : str = None

    def start_redis_listener(self):
        def run_async_listener():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self.redis_client.start_listener())
            except Exception as e:
                print(f"Error in Redis listener: {e}")
            finally:
                loop.close()
        
        self.redis_thread = threading.Thread(target=run_async_listener, daemon=True)
        self.redis_thread.start()
        print("Redis listener started in background thread")

    def draw_layout(self) -> None:
        self.camera_sensor = Sensor(175, 305, 175, 405, canvas = self.canvas)

        self.sensor_c4 = Sensor(495, 345, 495, 405, canvas = self.canvas)
        self.actuator_c4 = Actuator(450, 405, 500, 425, canvas = self.canvas)
        self.belt_c4 = Belt(450, 50, 500, 350, canvas = self.canvas, category = 4)

        self.sensor_c3 = Sensor(645, 345, 645, 405, canvas = self.canvas)
        self.actuator_c3 = Actuator(600, 405, 650, 425, canvas = self.canvas)
        self.belt_c3 = Belt(600, 50, 650, 350, canvas = self.canvas, category = 3)

        self.sensor_c2 = Sensor(795, 345, 795, 405, canvas = self.canvas)
        self.actuator_c2 = Actuator(750, 405, 800, 425, canvas = self.canvas)
        self.belt_c2 = Belt(750, 50, 800, 350, canvas = self.canvas, category = 2)

        self.sensor_c1 = Sensor(945, 345, 945, 405, canvas = self.canvas)
        self.actuator_c1 = Actuator(900, 405, 950, 425, canvas = self.canvas)
        self.belt_c1 = Belt(900, 50, 950, 350, canvas = self.canvas, category = 1)

        main_belt_sensors = [self.sensor_c1, self.sensor_c2, self.sensor_c3, self.sensor_c4]
        main_belt_actuators = [self.actuator_c1, self.actuator_c2, self.actuator_c3, self.actuator_c4]
        main_belt_belts = [self.belt_c1, self.belt_c2, self.belt_c3, self.belt_c4]
        self.main_belt = Belt(0, 350, CANVAS_WIDTH - GRID, 400, canvas = self.canvas, sensors = main_belt_sensors, actuators = main_belt_actuators, belts = main_belt_belts)

    def add_object(self) -> None:
        size = 40
        x = self.main_belt.x1 + (GRID - size) / 2
        y = self.main_belt.y1 + (GRID - size) / 2
        plant = Plant(x, y, size, canvas = self.canvas)
        self.main_belt.add_plant(plant)
        
        def upload_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(
                    self.redis_client.upload_image(
                        images_folder=Path(IMAGES_FOLDER), 
                        plant_id=plant.id,
                        callback=self.handle_plant_classification
                    )
                )
            except Exception as e:
                print(f"Error uploading image: {e}")
            finally:
                loop.close()
        
        threading.Thread(target=upload_async, daemon=True).start()
        self.plant_cnt += 1

    def handle_plant_classification(self, category: int = None, plant_id : int = None) -> None:
        if plant_id and category:
            plant = self.main_belt.plants.get(plant_id)
            if plant:
                plant.set_category(category)
                self.info_panel.increment_category(plant.category)
                self.control_panel.status_label.configure(text = f"Status: Classified Cat. {category}")

    def start_belt_movement(self) -> None:
        self.main_belt.start()
        self.belt_movement_status_id = self.after(50, self.start_belt_movement)

    def stop_belt_movement(self) -> None:
        self.main_belt.stop()
        if self.belt_movement_status_id:
            self.after_cancel(self.belt_movement_status_id)
            self.belt_movement_status_id = None

    def toggle_simulation(self) -> None:
        if not self.is_running:
            self.is_running = True
            self.control_panel.start_button.configure(text = "Stop Simulation", fg_color = '#c0392b', hover_color = '#e74c3c')
            self.control_panel.status_label.configure(text = "Status: Running")
            self.start_belt_movement()
        else:
            self.is_running = False
            self.control_panel.start_button.configure(text = "Start Simulation", fg_color = '#27ae60', hover_color = '#2ecc71')
            self.control_panel.status_label.configure(text = "Status: Stopped")
            self.stop_belt_movement()

    def reset_simulation(self) -> None:
        self.plant_cnt = 0
        self.is_running = True
        self.toggle_simulation()
        self.info_panel.reset_counters()
        self.canvas.delete("plant")
        self.main_belt.remove_all_plants()
    
    def update_belt_speed(self, new_speed: int) -> None:
        self.main_belt.x_speed = new_speed if self.main_belt.x_speed != 0 else 0
        self.main_belt.y_speed = new_speed if self.main_belt.y_speed != 0 else 0
        self.info_panel.update_belt_speed(new_speed)
    
    def remove_plant_from_category(self, category: int) -> None:
        self.info_panel.decrement_category(category)
        self.plant_cnt -= 1

    def destroy(self):
        print("Shutting down application...")
        self.redis_client.stop()
        if self.redis_thread and self.redis_thread.is_alive():
            self.redis_thread.join(timeout=2)
        super().destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()
