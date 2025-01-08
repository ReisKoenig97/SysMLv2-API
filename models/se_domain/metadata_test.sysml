package metadata_test{

    import SI::*; 
    import ScalarValues::*;

    metadata def PCB{
        doc /* This metadata def is mainly used to tag
             * certain elements of the model for better
             * grouping. 
             */
        //attribute isCritical : Boolean;
    }    

    @PCB about
        partA,
        partB;
     

    part def partA{
        attribute id : String;
        attribute len : Real; 
        //@PCB{isCritical = true;}
    }
    part def partB{
        attribute id : String;
        attribute len : Real; 
        //@PCB{isCritical = false;}
    }   
    part def partC{
        attribute id : String;
        attribute len : Real; 
    }   
}