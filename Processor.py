import unittest
from Unit import *

class Tests(unittest.TestCase):
    def setUp(self):
        pass

class Pipeline:
    #get all parameters from file and initialize particular pipeline
    def __init__(self):
        pass

    def __str__(self):
        pipeline_state=""
        pipeline_state += self.IF.__str__()
        pipeline_state += self.EXADD.__str__()
        return pipeline_state

    def update_pipeline(self):
        # Create All Units
        self.IF = Unit('IF',1,True)
        self.ID = Unit('ID',1,True)
        self.EXMULT = Unit('EXMULT',6,True)
        self.EXADD = Unit('EXADD',4,True)
        self.WB = Unit('WB',1,True)
        
        self.IF.add_new_inst('GG: L.D F1, 4(R4)',0)
        
        for i in range(1,11):
            print "-------------"+str(i)+"--------------"
            last_stage_instruction = self.EXADD.last_stage.instruction
            # Find whether there is instruction in last stage
            print self
            self.WB.update_unit(i)
            
            self.EXADD.update_unit(i)
            if(self.EXADD.is_last_stage_free() and last_stage_instruction!=None):
                print last_stage_instruction.operation+" completed at "+str(i)
            if(self.EXADD.is_free() and not self.IF.is_free()):
                self.EXADD.add_inst(self.IF,i)
                self.IF.update_unit(i)

if __name__ == '__main__':
    #unittest.main()
    p1 = Pipeline()
    p1.update_pipeline()
