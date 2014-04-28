import unittest
from Unit import *

class Tests(unittest.TestCase):
    def setUp(self):
        pass

class Pipeline:
    #get all parameters from file and initialize particular pipeline
    def __init__(self):
        self.read_files()

        # Create All Units
        self.IF = Unit('IF',1,True)
        self.ID = Unit('ID',1,True)
        self.EXMULT = Unit('EXMULT',6,True)
        self.EXADD = Unit('EXADD',4,True)
        self.WB = Unit('WB',1,True)
    
    def read_files(self):
        f = open('inst.txt')
        self.set_of_instructions = f.readlines()
        f.close()

    
    def __str__(self):
        pipeline_state=""
        pipeline_state += self.IF.__str__()
        pipeline_state += self.ID.__str__()
        pipeline_state += self.EXADD.__str__()
        pipeline_state += self.WB.__str__()
        return pipeline_state

    def update_pipeline(self):
        
        current_inst = 0
        self.IF.add_new_inst(self.set_of_instructions[current_inst].strip(),0)
        current_inst +=1

        #while(1):
        for i in range(1,100):
            print "-------------"+str(i)+"--------------"
            print self
            last_stage_instruction = self.WB.last_stage.instruction
            self.WB.update_unit(i)
            # Find whether there is instruction in last stage
            if(self.WB.is_last_stage_free() and last_stage_instruction!=None):
                print last_stage_instruction.operation+" completed at "+str(i)

            if(self.WB.is_free() and not self.EXADD.is_last_stage_free()):
                self.WB.add_inst(self.EXADD,i)
            
            self.EXADD.update_unit(i)
            if(self.EXADD.is_free() and not self.ID.is_free()):
                self.EXADD.add_inst(self.ID,i)

            self.ID.update_unit(i)
            if(self.ID.is_free() and not self.IF.is_free()):
                self.ID.add_inst(self.IF,i)

            self.IF.update_unit(i)
            if(self.IF.is_free()):
                self.IF.add_new_inst(self.set_of_instructions[current_inst].strip(),i)
                current_inst +=1
                
            if(current_inst==len(self.set_of_instructions)):
                break
                

if __name__ == '__main__':
    #unittest.main()
    p1 = Pipeline()
    p1.update_pipeline()
    
