package DroneExample {

    public import SI::*; 
    public import ISQ::*; 
    public import PartDefinitions::*; 
    public import PartDefinitions::Drone::*; // for concerns 
    public import Views::*; // for views and viewpoints
    public import ModelingMetadata::*; // includes the Metadata SysML Library (comes with SysMLv2)
    public import ScalarValues::*; // Real, ... includes the ScalarValues SysML Library (comes with SysMLv2)
    public import Constraints::*; // for constraints 

    item def Person;
    item def Commands;

    // PACKAGE APPROACH using metadata to tag certain elements 
    metadata def PCBDesign{
        attribute isCritical : Boolean; 
    }
    metadata def PCB;
    //used to "tag" the elements 
    @PCBDesign about 
        DroneExample::PartDefinitions::Drone::FlightController,
        DroneExample::PartDefinitions::Drone::FlightController; 
    
    @PCB about 
        DroneExample::PartDefinitions::Drone::ElectronicSpeedController; 

    package PartDefinitions{
        part def Drone {
            attribute id = "drone-001";
            attribute name = "Drone";
            attribute description = "Hello Drone";
            attribute mass : MassValue; //actual mass of the drone
            
            constraint massCheck : MassConstraint{
                in partMasses = (fc.mass, cs.mass, enc.mass, motor.mass, prop.mass, 
                cam.mass, batt.mass, pdb.mass, esc.mass, trans.mass, rec.mass, gpsm.mass);
                in massLimit = 1000[g];
            }

            part fc : FlightController;
            part cs : Chassis; 
            part enc : Enclosure; 
            part motor : Motor[4]; 
            part prop : Propellor[4];
            part cam : Camera;   
            part batt : Battery; 
            part pdb : PowerDistributionBoard; 
            part esc : ElectronicSpeedController; 
            part trans : Transmitter; 
            part rec : Receiver; 
            part gpsm : GPSModule; 

            part def 'Systems Engineer';
            part def 'Electronic Engineer';
            part def 'Software Engineer';
            part def 'Mechanical Engineer';

            metadata def 'PCB'{
                attribute isMandatory : Boolean; 
                attribute isCustom : Boolean; 
            }  

            ref item pilot : Person; //system model may reference discrete items that interact with or pass through the system
            ref item cmds : Commands; 

            connect fc to cs;
            connect enc to cs;  
            connect motor to cs;
            connect prop to motor; 
            connect cam to cs; 
            connect batt to cs; 
            connect pdb to cs; 
            connect esc to cs; 
            connect trans to cs; 
            connect rec to cs; 
            connect gpsm to cs;  

            part def FlightController{
                attribute id = "abc123"; 
                attribute name = "fc-123";
                attribute mass : MassValue; 
                attribute description = "";
                
                part def pcb {
                    attribute id = "pcb-001-123"; 
                    attribute name = "PCB-123";
                    attribute description = "";
                    attribute mass : MassValue; 
                    attribute max_length = 70[mm]; 
                    attribute max_width = 70[mm];  
                
                }
            }

            part def Chassis {
                attribute id = "chassis-001"; 
                attribute name = "Chassis";
                attribute mass : MassValue; 
                attribute description = "";
            }

            part def Enclosure {
                attribute id = "enclosure-001";
                attribute name = "Enclosure XPF01a";
                attribute description = "Casing/Enclosure";
                attribute mass : MassValue; 
                attribute max_length = 200[mm];
                attribute max_width = 200[mm];
                attribute max_height = 80[mm];
                
            }

            part def Motor{
                attribute id = "motor-001";
                attribute name = "Brushless Motor";
                attribute description = "";
                attribute mass : MassValue; 
                attribute max_speed = 15000[1/min^-1];
                attribute max_voltage = 11.1[V];
                attribute max_current = 30[A];
            }

            part def Propellor{
                attribute id = "propellor-001";
                attribute name = "propellor";
                attribute description = "";
                attribute mass : MassValue; 

                part blade : Blade[2..4]; 

                part def Blade{
                    attribute id = "blade-001";
                    attribute name = "blade";
                    attribute description = "";
                    attribute mass : MassValue; 
                }
            }

            part def Camera{
                attribute id = "camera-001";
                attribute name = "4K Camera";
                attribute description = "";
                attribute mass : MassValue; 
                attribute resolution = "3840x2160";
                attribute max_framerate = 60;
                attribute lens_angle = 120[degree];
            }

            part def Battery{
                attribute id = "battery-001";
                attribute name = "LiPo Battery 3S";
                attribute description = "";
                attribute mass : MassValue; // e.g. 180[g]
                attribute capacity = 2200[milli*ampere*h];
                attribute voltage = 11.1[V];
            }

            part def PowerDistributionBoard{
                attribute id = "pdb-001";
                attribute name = "Power Distribution Board";
                attribute description = "";
                attribute mass : MassValue; 
                attribute max_current = 120[A];
                attribute min_voltage_input = 11.1 [V]; 
                attribute max_voltage_input = 14.8 [V]; 
            }

            part def ElectronicSpeedController{
                attribute id = "esc-001";
                attribute name = "ESC 30A";
                attribute description = "";
                attribute mass : MassValue; 
                attribute max_current = 30[A];
                attribute input_voltage = 11.1[V];
                attribute pwm_frequency = 500[Hz];
            }

            part def Transmitter{
                
                attribute id = "transmitter-001";
                attribute name = "FPV Transmitter";
                attribute description = "";
                attribute mass : MassValue; 
                attribute frequency = "5.8[GHz]";
                attribute power = 600[milli*W];
                attribute range = 1000[m];
            }

            part def Receiver{
                attribute id = "receiver-001";
                attribute name = "FPV Receiver";
                attribute description = "";
                attribute mass : MassValue; 
                attribute frequency = "5.8[GHz]";
                attribute sensitivity = -90[dB*milli*W];
                attribute channels = 40;
            }

            part def GPSModule{
                attribute id = "gpsmodule-001";
                attribute name = "GPS MX2";
                attribute description = "";
                attribute mass : MassValue; 

                part gps_pcb : GPSModulePCB; 
                part ss : SpeedSensor; 
                part hs : HeightSensor; 
                part ps : PositionSensor;

                part def GPSModulePCB{
                    doc /* This can be a customized PCB */
                    attribute id = "gpsmodule-pcb-001";
                    attribute name = "Custom PCB";
                    attribute description = "";
                    attribute mass : MassValue; 
                }

                part def SpeedSensor {
                    attribute id = "speed-sensor-001";
                    attribute name = "Speed Sensor";
                    attribute description = "";
                    attribute mass : MassValue; 
                    attribute max_range = 60[km/h];
                }

                part def HeightSensor {
                    attribute id = "height-sensor-001";
                    attribute name = "Height Sensor";
                    attribute description = "";
                    attribute mass : MassValue; 
                    attribute max_range = 1000[m];
                }

                part def PositionSensor {
                    attribute id = "position-sensor-001";
                    attribute name = "Position Sensor";
                    attribute description = "";
                    attribute mass : MassValue; 
                    attribute technology = "GPS";
                }  
            } 
        }  
    }

    package Constraints{
        constraint def MassConstraint{
            in partMasses : MassValue[0..*];
            in massLimit : MassValue;

            sum(partMasses) <= massLimit
        }
    }
}
