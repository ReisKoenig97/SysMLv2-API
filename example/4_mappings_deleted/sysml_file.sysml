package AUTOSAR{
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
        SHORT-NAME = "Component_1_new";
        PORTS{}
        INTERNAL-BEHAVIOURS{}
    }
}