package DroneExample {

    public import SI::*; 
    public import RequirementsDefinitions::*; 
    public import PartDefinitions::*; 
    public import PartDefinitions::Drone::*; // for concerns 
    public import Views::*; // for views and viewpoints
    public import ModelingMetadata::*; // includes the Metadata SysML Library (comes with SysMLv2)
    public import ScalarValues::*; // Real, ... includes the ScalarValues SysML Library (comes with SysMLv2)
    
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
            attribute mass : MassValue; 

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
            part def 'E/E Engineer';
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

    // requirement def is a special kind of constraint def
    package RequirementsDefinitions{
        // For Units and Values look at Domain Library inside the SysMLv2 Release 
        // <'1'> can be used as the ID or label followed by name of req
        requirement def <'1'> MassLimitationRequirement{
            doc /* The actual mass shall be less than or equal to the required mass. */
            attribute massActual : MassValue; //MassValue is from the ISQ:Base Standardlibrary or SI (unit library)
            attribute massReqd : MassValue; 
            require constraint {massActual <= massReqd}
        } 

        requirement def <'2'> CurrentLimitationRequirement{
            doc /* The total current draw of all components shall not exceed the maximum allowable current. */
            attribute currentActual : ElectricCurrentValue; 
            attribute currentMaxAllowed : ElectricCurrentValue; 
            require constraint {currentActual <= currentMaxAllowed}
        } 

        requirement def <'3'> VoltageRangeLimitationRequirement{
            doc /* The operating voltage of the drone must remain within the allowable range. */
            attribute voltageActual : ElectricPotentialUnit; 
            attribute voltageMinAllowed : ElectricPotentialUnit; 
            attribute voltageMaxAllowed : ElectricPotentialUnit; 
            require constraint {voltageMinAllowed <= voltageActual <= voltageMaxAllowed}
        } 
        requirement def <'4'> TemperatureRangeRequirement {
            doc /* The drone and its components must operate within the specified temperature range. */
            attribute temperatureActual : TemperatureValue; 
            attribute temperatureMinAllowed : TemperatureValue; 
            attribute temperatureMaxAllowed : TemperatureValue; 
            require constraint {temperatureMinAllowed <= temperatureActual <= temperatureMaxAllowed}
        } 
         requirement def <'5'> FlightTimeRequirement {
            doc /* The drone shall be capable of maintaining flight for at least the specified duration. */
            attribute flightTimeActual : DurationValue; 
            attribute flightTimeMinRequired : DurationValue; 
            require constraint {flightTimeActual >= flightTimeMinRequired}
        }
        requirement def <'6'> PayloadCapacityRequirement {
            doc /* The drone shall be able to carry the required payload weight without exceeding its limits. */
            attribute payloadMassActual : MassValue; 
            attribute payloadMassMaxAllowed : MassValue; 
            require constraint {payloadMassActual <= payloadMassMaxAllowed}
        }
        requirement def <'7'> CommunicationRangeRequirement {
            doc /* The drone's transmitter and receiver must ensure communication does not exceed the maximum allowable range. */
            attribute communicationRangeActual : LengthValue; 
            attribute communicationRangeMaxAllowed : LengthValue; 
            require constraint {communicationRangeActual <= communicationRangeMaxAllowed}
        }

        requirement def <'8'> GPSAccuracyRequirement {
            doc /* The GPS module must provide position data within the specified accuracy range. */
            attribute gpsAccuracyActual : LengthValue; 
            attribute gpsAccuracyMaxAllowed : LengthValue; 
            require constraint {gpsAccuracyActual <= gpsAccuracyMaxAllowed}
        }
        requirement def <'9'> MotorSpeedRequirement {
            doc /* The motors shall operate within the specified speed range under normal conditions. */
            attribute motorSpeedActual : AngularVelocityValue; 
            attribute motorSpeedMaxAllowed : AngularVelocityValue; 
            require constraint {motorSpeedActual <= motorSpeedMaxAllowed}
        }
    }

    package Requirements{
        doc /* Used RequirementsDefinition are specified here with concrete values. 
        A requirement is the usage of a requirement definition */

        requirement DroneSpecification{
            subject drone : Drone; // has to be included from the import PartDefinitions::*; 

            requirement <'1'> droneTotalMass : MassLimitationRequirement{
                doc /* The total mass of the mass of the drone shall be less than or equal to required mass.
                Assume total mass includes the maximum weight of the payload.*/
                attribute redefines massReqd = 400[g]; 
                attribute :> massActual default drone.cs.mass + drone.enc.mass + drone.motor.mass + drone.prop.mass 
                + drone.cam.mass + drone.batt.mass + drone.pdb.mass + drone.esc.mass + drone.trans.mass 
                + drone.rec.mass + drone.gpsm.mass; 
            }

            requirement <'2'> droneTotalPayload : PayloadCapacityRequirement{
                doc /* Total mass of the payload shall be less than or equal to the maximum allowed mass.*/
                attribute :> payloadMassMaxAllowed = 150[g]; // :> means specializes and :>> means redefines 
                attribute :> payloadMassActual default = 0[g]; 

                // (Metadata) StatusInfo is contained in ModelingMetadata library
                // StatusKind has values for open, closed, tbd, tbr, tbd
                @StatusInfo{ //@ is equivalent to 'metadata'
                    status = StatusKind::closed; 
                    originator = "Tom"; 
                    owner = "Paul";
                }
                // (Metadata) Rationale is used to explain a choice or other decision made related to the annotated elemen
                @Rationale{
                    text = "We need this payload requirement in case for using additional sensors or modules"; 
                }

            }
        }
    }
}
