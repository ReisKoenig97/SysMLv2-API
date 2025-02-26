package metadata_test{
    
    public import SI::*; 
    public import ScalarValues::*; 

    metadata def PCB{
        doc /* This metadata def is mainly used to tag
            * certain elements of the model for better
            * grouping. 
            */
    }    

    metadata def UUID{
        uuid : String;
    }

    @PCB about
        partA,
        partB;
    
    part def partA{
        attribute id = "8.0.6";
        attribute mass = 50.1; // 50.1 
    }
    part def partB{
        attribute id = "KiCad2025_1234"; //{@UUID{uuid="001";}}
        attribute len = 12.5[m];
    }   
    part def partC{
        attribute id = "KiCad";
        attribute len = "STEP_AgriUAV2025";
        attribute lenA = 7.43[m];
    }   
    part def partD{
        attribute id = "48616465-735f-4707-926f-6a6563742e6b";
    }
}
