package metadata_test{
    
    public import SI::*; 
    public import ScalarValues::*; 

    metadata def PCB{
        doc /* This metadata def is mainly used to tag
            * certain elements of the model for better
            * grouping. 
            */
    }    
    
    @PCB about
        partA,
        partC;
    
    part def partA{
        attribute id = "Hades_project02";
        attribute mass = 12.2; // 50.1
    }
    part def partB{
        attribute id = "TViPro1_WS2425_HA2_Aufgabe4_Gruppe311_1.stp";
        attribute len = 12.5[m];
    }   
    part def partC{
        attribute id = "TViPro1_WS2425_HA2_Aufgabe4_Gruppe311_1.stp";
        attribute len = "TRANSPORTBOX";
        attribute lenA = 7.43[m];
    }   
    part def partD{
        attribute id = "abc12312";
    }
}
