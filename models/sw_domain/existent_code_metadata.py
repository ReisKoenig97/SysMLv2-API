# This file represents the scenario that source code already exists and is already using metadata annotations.
from typing import Any

# NOTE: 
# Use Case: The Software Engineer has to code the metadata usage himself which means if he wants to make the code 
# dependent on e.g. sysmlv2 model (sysmlv2 model changes -> code values tagged with metadata changes -> outcome changes)
# 
# metadata can here only be added before a class definition and with given "def metadata"

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

@metadata("mass", "150.70", "g", "float", "PCB", "Motor.mass")
@metadata("speed", "100", "rpm", "int", "PCB", "Motor.speed")
@metadata("current", "30", "A", "string", "PCB", "Motor.current")
class Motor:
    def __init__(self, motortype: str, power: float, voltage: str, mass: float, speed: float, torque: float, current: float, efficiency: float):
        self.motortype = motortype,
        self.power = power, 
        self.voltage = voltage,
        self.mass = mass,
        self.speed = speed,
        self.torque = torque,
        self.current = current, 
        self.efficiency = efficiency

@metadata("mass", "35", "g", "float", "PCB", "Blade.mass")
class Blade:
    def __init__(self, mass : float, length : float):
        self.mass = mass, 
        self.length = length

def main():
    motorA = Motor(motortype="brushless", power=50.0, voltage="12V", mass=150.70, speed=100.0, torque=0.5, current=2.0, efficiency=0.85)
    print(motorA.metadata)
    bladeA = Blade(mass=30, length=30) #mass=30, length=30

    print("BladeA Metadata: ", bladeA.metadata)

if __name__ == "__main__":
    main()
