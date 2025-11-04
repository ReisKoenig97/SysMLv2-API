package sysml_elements {

    part def sysml_elem_m2o_nvc {
        attribute sysml_attrib_1 = "snd_Value_1";
        attribute sysml_attrib_2 = "/PortInterfaces/Comp_1_to_Comp_2/Comp_1_value_1";
        attribute sysml_attrib_3 = "Component_1";
    }

    part def sysml_elem_m2o_vc {
        attribute sysml_attrib_1 = "newSndValue1sysml";
        attribute sysml_attrib_2 = "Path/To/Whereever";
        attribute sysml_attrib_3 = "Component1NewName";
    }

    part def sysml_elem_o2o_nvc {
        attribute sysml_attrib_1 = "snd_Value_1";
        attribute sysml_attrib_3 = "Component_1";
    }

    part def sysml_elem_o2o_vc {
        attribute sysml_attrib_1 = "snd_Value_1_notUpdated";
        attribute sysml_attrib_3 = "Component_1_notUpdated";
        attribute sysml_attrib_2 = "/PortInterfaces/Comp_1_to_Comp_2/Comp_1_value_1_new";
    }

}
