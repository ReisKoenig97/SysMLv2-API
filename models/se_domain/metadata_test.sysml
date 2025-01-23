    package metadata_test{

        import SI::*; 
        import ScalarValues::*;

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
            attribute len : Real {@UUID {uuid = "123e4567-e89b-12d3-a456-426614174000";}}
            attribute mass : Real; 
        }
        part def partB{
            attribute id : String {@UUID {uuid = "124e4567-e89b-12d3-a456-426614174000";}}
            attribute len : Real {@UUID {uuid = "125e4567-e89b-12d3-a456-426614174000";}}
            attribute lenA = 7.43;  
        }   
        part def partC{
            attribute id : String;
            attribute len : Real; 
        }   
    }