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
        attribute id = "Hades_project";
        attribute mass = 50.1; // 50.1 
    }
    part def partB{
        attribute id = "KiCad2";
        attribute len = 12.5[m];
    }   
    part def partC{
        attribute id = "KiCad";
        attribute len : Real; 
        attribute lenA : Real;  
    }   
    part def partD{
        attribute id = "48616465-735f-4707-926f-6a6563742e6b";
    }
}
