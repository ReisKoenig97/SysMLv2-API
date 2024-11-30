package DronePartDefinitions {

    import SI::*; 

    // TODO; max_values als constraint oder requirement
    part def Drone {
        attribute id = "drone-001";
        attribute name = "Drone";
        attribute description = "Hello Drone";

        attribute totalMass : MassValue; 

        part fc : FlightController;
        part enc : Enclosure; 
        part motor : Motor[4]; 
        part prop : Propellor[4];
        part cam : Camera;   
        part batt : Battery; 
        part pdp : PowerDistributionPanel; 
        part esc : ElectronicSpeedController; 
        part trans : Transmitter; 
        part rec : Receiver; 
        part ss : SpeedSensor; 
        part hs : HeightSensor; 
        part ps : PositionSensor; 

        // constraint is the usage of constraint definition which may be true or false in given context 
        constraint MassConstraint{
            in partMasses = (fc.mass + enc.mass + motor.mass + prop.mass + cam.mass + batt.mass + pdp.mass + esc.mass + trans.mass + rec.mass + ss.mass + hs.mass + ps.mass);
            in totalMassLimit = 250[g]; //dji mini 3 = 249g 
        }


        // PART DEFINITIONS 

        part def FlightController{
            attribute id = "abc123"; 
            attribute name = "PCB-123";
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
            attribute mass : MassValue; 
            attribute capacity = 2200[milli*ampere*h];
            attribute voltage = 11.1[V];
            //attribute weight = 180[g]; //eg constraint or requirements
        }

        part def PowerDistributionPanel{
            attribute id = "pdp-001";
            attribute name = "Power Distribution Panel";
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
/*

// requirement def is a special kind of constraint def
package DroneRequirements{
    import DronePartDefinitions::*; 
    

    // <'1'> can be used as the ID or label followed by name of req
    requirement def <'1'> MassLimitationRequirement{
        doc /* The actual mass shall be less than or equal
            * to the required mass. 

        subject drone : Drone; 
            
        //attribute redefines massActual  = drone.totalMass  
        attribute massActual : MassValue; //von ISQ:Base Standardlibrary 
        attribute massReqd : MassValue; 

        require constraint {massActual <= massReqd}
    } 
}
*/
constraint def MassConstraint{
    import SI::*; 
    import ISQ::*; 
    import ScalarFunctions::*; 

    in partMasses : MassValue[0..*]; 
    in totalMassLimit : MassValue; 
    partMasses <= totalMassLimit  
}