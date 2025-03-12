
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



@metadata("id", "123a", "", "string", "PCBDesign", "FlightController.id")
@metadata("name", "fc-123", "", "string", "PCBDesign", "FlightController.name")
@metadata("description", "", "", "string", "PCBDesign", "FlightController.description")
@metadata("id", "pcb-001-123", "", "string", "PCBDesign", "FlightController.id")
@metadata("name", "PCB-123", "", "string", "PCBDesign", "FlightController.name")
@metadata("description", "", "", "string", "PCBDesign", "FlightController.description")
@metadata("max_length", "70", "mm", "int", "PCBDesign", "FlightController.max_length")
@metadata("max_width", "70", "mm", "int", "PCBDesign", "FlightController.max_width")

class FlightController:
    def __init__(self, **kwargs):
        self.id = "abc123"
        self.name = "fc-123"
        self.description = ""
        self.id = "pcb-001-123"
        self.name = "PCB-123"
        self.description = ""
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
        
