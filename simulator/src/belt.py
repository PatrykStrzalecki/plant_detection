import customtkinter as ctk
from sensor import Sensor
from actuator import Actuator
from plant import Plant

class Belt:
    def __init__(
            self, 
            x1 : int, 
            y1 : int, 
            x2 : int, 
            y2 : int, 
            speed : int = 2,
            color : str = "#18191a",
            category : int = 0, 
            canvas : ctk.CTkCanvas = None, 
            sensors : list['Sensor'] = None,
            actuators : list['Actuator'] = None,
            belts : list['Belt'] = None,
    ):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.width = y2 - y1 if y2 - y1 < x2 - x1 else x2 - x1
        self.length = x2 - x1 if x2 - x1 < y2 - y1 else y2 - y1
        self.category = category
        self.color = color
        self.canvas = canvas
        self.x_speed = speed if x2 - x1 > y2 - y1 else 0
        self.y_speed = -speed if y2 - y1 > x2 - x1 else 0
        self.id = self.canvas.create_rectangle(x1, y1, x2, y2, fill = self.color, outline = "#000000", width = 2, tags = "belt")
        self.sensors = sensors if sensors else []
        self.actuators = actuators if actuators else []
        self.belts = belts if belts else []
        self.plants : dict[int, Plant] = {}
        self.is_running = False
        self.mount_sensors()
        self.mount_actuators()
        self.mount_belts()

    def add_plant(self, plant : Plant = None) -> None:
        if plant:
            self.plants.setdefault(plant.id, plant)

    def move_plants(self) -> None:
        for plant in self.get_plants():
            plant.move(x_speed=self.x_speed, y_speed=self.y_speed)
            if plant.x > self.x2 or plant.y < self.y1:
                self.canvas.delete(plant.id)
                del self.plants[plant.id]

    def start(self) -> None:
        self.is_running = True
        self.move_plants()
        for belt in self.belts:
            belt.start()
        for sensor in self.sensors:
            plant = sensor.is_active_sensor(list(self.plants.values()))
            if plant and plant.category == sensor.category:
                self.actuators[sensor.category - 1].activate()
                self.canvas.after(500, self.actuators[sensor.category - 1].deactivate)
                plant = self.plants.pop(plant.id)
                self.belts[sensor.category - 1].add_plant(plant)

    def stop(self) -> None:
        self.is_running = False

    def remove_all_plants(self) -> None:
        for plant in self.plants.values():
            self.canvas.delete(plant.id)
        self.plants.clear()

    def get_plant_count(self) -> int:
        return len(self.plants)
    
    def get_plants(self) -> list[Plant]:
        return list(self.plants.values())

    def mount_sensors(self) -> None:
        for category, sensor in enumerate(self.sensors, start = 1):
            sensor.mount_sensor()
            sensor.set_category(category)

    def mount_actuators(self) -> None:
        for category, actuator in enumerate(self.actuators, start = 1):
            actuator.mount_actuator()
            actuator.category = category

    def mount_belts(self) -> None:
        for category, belt in enumerate(self.belts, start = 1):
            belt.set_category(category)

    def set_category(self, category : int = 0) -> None:
        self.category = category