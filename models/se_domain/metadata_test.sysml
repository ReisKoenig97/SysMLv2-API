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
        private import SI::mm; 
        attribute id : String;
        attribute mass = 50.1; // 50.1 
    }
    part def partB{
        attribute id = "Pcbnew";
        attribute len = 7.43[mm];
    }   
    part def partC{
        attribute id : String;
        attribute len : Real; 
        attribute lenA = 10.12[mm];  
    }   
    part def partD{
        attribute id = "Hades_project";
    }
}
