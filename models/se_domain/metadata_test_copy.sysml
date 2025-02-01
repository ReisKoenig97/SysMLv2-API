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
            attribute id : String;
            attribute len : Real; 
            attribute mass = 50.1; 
        }
        part def partB{
            attribute id : String; 
            attribute len : Real; 
        }   
        part def partC{
            attribute id : String;
            attribute len : Real; 
            attribute lenA = "7.43";  
        }   
        part def partD{
            attribute id : String;
        }
    }
