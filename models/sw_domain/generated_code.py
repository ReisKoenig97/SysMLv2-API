
# Generated from SysMLv2 model
from typing import Any

def metadata(name: str, value: Any, unit: str, dataType: str, metadataTag: str = None, elementPath: str = None):
    def wrapper(cls):
        if not hasattr(cls, 'metadata'):
            cls.metadata = []
        cls.metadata.append({
            "name": name,
            "value": value,
            "unit": unit,
            "dataType": dataType,
            "metadata_tag": metadataTag,
            "elementPath": elementPath or f"{cls.__name__}.{name}",
        })
        return cls
    return wrapper


@metadata("id", "test123", "", "string", "PCB", "FlightController.id")
@metadata("name", "fc-123", "", "string", "PCB", "FlightController.name")
@metadata("description", "", "", "string", "PCB", "FlightController.description")
@metadata("id", "STEP_AgriUAV2025", "", "string", "PCB", "FlightController.id")
@metadata("name", "PCB-123", "", "string", "PCB", "FlightController.name")
@metadata("description", "150.7", "", "float", "PCB", "FlightController.description")
@metadata("max_length", "70", "mm", "int", "PCB", "FlightController.max_length")
@metadata("max_width", "70", "mm", "int", "PCB", "FlightController.max_width")

class FlightController:
    def __init__(self, **kwargs):
        self.id = "test123"
        self.name = "fc-123"
        self.description = ""
        self.id = "STEP_AgriUAV2025"
        self.name = "PCB-123"
        self.description = "150.7"
        self.max_length = "70"
        self.max_width = "70"
        


@metadata("id", "esc-001", "", "string", "PCB", "ElectronicSpeedController.id")
@metadata("name", "ESC 30A", "", "string", "PCB", "ElectronicSpeedController.name")
@metadata("description", "", "", "string", "PCB", "ElectronicSpeedController.description")
@metadata("max_current", "30", "A", "int", "PCB", "ElectronicSpeedController.max_current")
@metadata("input_voltage", "11.1", "V", "float", "PCB", "ElectronicSpeedController.input_voltage")
@metadata("pwm_frequency", "500", "Hz", "int", "PCB", "ElectronicSpeedController.pwm_frequency")

class ElectronicSpeedController:
    def __init__(self, **kwargs):
        self.id = "esc-001"
        self.name = "ESC 30A"
        self.description = ""
        self.max_current = "30"
        self.input_voltage = "11.1"
        self.pwm_frequency = "500"
        


@metadata("id", "motor-001", "", "string", "PCB", "Motor.id")
@metadata("name", "Brushless Motor", "", "string", "PCB", "Motor.name")
@metadata("description", "", "", "string", "PCB", "Motor.description")
@metadata("max_speed", "15000", "1/min^-1", "int", "PCB", "Motor.max_speed")
@metadata("max_voltage", "11.1", "V", "float", "PCB", "Motor.max_voltage")
@metadata("max_current", "30", "A", "int", "PCB", "Motor.max_current")

class Motor:
    def __init__(self, **kwargs):
        self.id = "motor-001"
        self.name = "Brushless Motor"
        self.description = ""
        self.max_speed = "15000"
        self.max_voltage = "11.1"
        self.max_current = "30"
        


@metadata("id", "enclosure-001", "", "string", "PCB", "Enclosure.id")
@metadata("name", "Enclosure XPF01a", "", "string", "PCB", "Enclosure.name")
@metadata("description", "Casing/Enclosure", "", "string", "PCB", "Enclosure.description")
@metadata("max_length", "200", "mm", "int", "PCB", "Enclosure.max_length")
@metadata("max_width", "200", "mm", "int", "PCB", "Enclosure.max_width")
@metadata("max_height", "80", "mm", "int", "PCB", "Enclosure.max_height")

class Enclosure:
    def __init__(self, **kwargs):
        self.id = "enclosure-001"
        self.name = "Enclosure XPF01a"
        self.description = "Casing/Enclosure"
        self.max_length = "200"
        self.max_width = "200"
        self.max_height = "80"
        

