package DroneModel {

    part def Drone {
        attribute name = "Drone";

        part controller : FlightController;
        part motor : Motor;

        connect controller.ctrl_out to motor.ctrl_in;
        connect controller.pwr_out to motor.pwr_in;
    }

    part def FlightController {
        attribute id = "fc-001";

        port ctrl_out : ControlSignal;
        port pwr_out : Power;
    }

    part def Motor {
        attribute id = "motor-001";

        port ctrl_in : ControlSignal;
        port pwr_in : Power;
    }

    item def ControlSignal;
    item def Power;
}
