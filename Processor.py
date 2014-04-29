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
        self.EXMULT = Unit('EXMULT',self.EXMULT_cycles,self.EXMULT_pipelined)
        self.EXADD = Unit('EXADD',self.EXADD_cycles,self.EXADD_pipelined)
        self.EXDIV = Unit('EXDIV',self.EXDIV_cycles,self.EXDIV_pipelined)
        self.WB = Unit('WB',1,True)
    
    def read_files(self):
        # Read all instructions
        f = open('inst.txt')
        self.set_of_instructions = f.readlines()
        f.close()
        
        # Read config file
        f = open('config.txt')
        lines = f.readlines()
        EXADD_params = lines[0].split(':')[1].strip()
        EXMULT_params = lines[1].split(':')[1].strip()
        EXDIV_params = lines[2].split(':')[1].strip()
        
        self.EXADD_cycles = int(EXADD_params.split()[0].strip(','))
        self.EXADD_pipelined = EXADD_params.split()[1].upper()=='YES'
        
        self.EXMULT_cycles = int(EXMULT_params.split()[0].strip(','))
        self.EXMULT_pipelined = EXMULT_params.split()[1].upper()=='YES'
        
        self.EXDIV_cycles = int(EXDIV_params.split()[0].strip(','))
        self.EXDIV_pipelined = EXDIV_params.split()[1].upper()=='YES'
        
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
        for i in range(1,10):
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
            self.EXMULT.update_unit(i)
            self.EXDIV.update_unit(i)
            self.ID_to_EX(i)

            self.ID.update_unit(i)
            if(self.ID.is_free() and not self.IF.is_free()):
                self.ID.add_inst(self.IF,i)

            self.IF.update_unit(i)
            if(self.IF.is_free() and current_inst!=len(self.set_of_instructions)):
                self.IF.add_new_inst(self.set_of_instructions[current_inst].strip(),i)
                current_inst +=1
                
        
    def ID_to_EX(self,clk):
        if(not self.ID.is_free()):
            if(self.ID.last_stage.instruction.exunit=='EXADD'):
                if(self.EXADD.is_free()):
                    self.EXADD.add_inst(self.ID,clk)
            

if __name__ == '__main__':
    #unittest.main()
    p1 = Pipeline()
    p1.update_pipeline()
    
