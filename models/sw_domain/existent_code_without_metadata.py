# This file represents the scenario that source code already exists and is already using metadata annotations.
from typing import Any


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
