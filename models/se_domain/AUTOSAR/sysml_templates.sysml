port def Port{
    attribute type: String;
    attribute 
}

part def SWC{
    attribute Type: String;
    attribute SHORT-NAME: String;
    package PORTS{
        port Ports[]: Port
    }
    package behaviours{
        part behaviours[0..*]: internalBehaviour
    }
}


part mySWC : SWC{

}

connection NAME {
    end Instanz.port
    end Instanz.port
}


part def SWC{
    attribute Tag: String;
    attribute SHORT-NAME: String;
    part PORTS{
        part Port[0..*] : PORT;
    }
    part INTERNAL-BEHAVIOURS{
        part INTERNAL-BEHAVIOUR[0..*] : INTERNAL-BEHAVIOUR;
    }
}

part Component_1 : SWC{
    Tag = "APPLICATION-SW-COMPONENT-TYPE";
    SHORT-NAME = "Component_1";
    PORTS{
        PORT[0]:PORT as snd_Value_1{
            TAG = "P-PORT-PROTOTYPE";
            ...
        }
        PORT[1]:PORT as rcv_mode_switch_interface{
            ...
        }
    }
    INTERNAL-BEHAVIOURS{
        ...
    }
}