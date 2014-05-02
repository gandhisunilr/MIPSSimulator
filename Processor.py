from Unit import *
from Instruction import *

class Pipeline:
    #get all parameters from file and initialize particular pipeline
    def __init__(self):
        self.read_files()
        self.all_inst_fetched = False

        # Create All Units
        self.IF = Unit('IF',1,True)
        self.ID = Unit('ID',1,True)
        self.EXMULT = Unit('EXMULT',self.EXMULT_cycles,self.EXMULT_pipelined)
        self.EXADD = Unit('EXADD',self.EXADD_cycles,self.EXADD_pipelined)
        self.EXDIV = Unit('EXDIV',self.EXDIV_cycles,self.EXDIV_pipelined)
        self.WB = Unit('WB',1,True)
    
    def __str__(self):
        pipeline_state=""
        pipeline_state += self.IF.__str__()+"\n"
        pipeline_state += self.ID.__str__()+"\n"
        pipeline_state += self.EXADD.__str__()+"\n"
        pipeline_state += self.EXMULT.__str__()+"\n"
        pipeline_state += self.EXDIV.__str__()+"\n"
        pipeline_state += self.WB.__str__()+"\n"
        return pipeline_state

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

    def update_pipeline(self):        
        
        current_inst = 0
        first_instruction = Instruction(self.set_of_instructions[current_inst].strip())
        self.IF.add_new_inst(first_instruction)
        current_inst +=1
        print "-------------1--------------"
        print self
        
        for i in range(2,14):
            print "-------------"+str(i)+"--------------"
            self.WB.execute_unit()
            self.WB.remove_all_completed()
            self.EXADD.execute_unit()
            if(self.WB.is_free()):
                EX_complete_inst =self.EXADD.get_completed_inst()
                if(EX_complete_inst!=False):
                    if(self.WB.add_new_inst(EX_complete_inst)==False):
                        print "Debugging Time"
            
            self.ID.execute_unit()
            ID_inst =  self.ID.peek_completed_inst()
            if(self.EXADD.is_free()):
                ID_complete_inst =self.ID.get_completed_inst()
                if(ID_complete_inst!=False):
                    if(self.EXADD.add_new_inst(ID_complete_inst)==False):
                        print "Debugging Time"
            
            self.IF.execute_unit()
            if(self.ID.is_free()):
                IF_complete_inst =self.IF.get_completed_inst()
                if(IF_complete_inst!=False):
                    if(self.ID.add_new_inst(IF_complete_inst)==False):
                        print "Debugging Time"

            if(self.IF.is_free() and self.all_inst_fetched==False):
                new_inst = Instruction(self.set_of_instructions[current_inst].strip())
                current_inst +=1
                if(new_inst.operation!='HLT'):
                    if(self.IF.add_new_inst(new_inst)==False):
                        print "Debugging Time"
                else:
                    self.all_inst_fetched=True
            print self
            

if __name__ == '__main__':
    #unittest.main()
    p1 = Pipeline()
    p1.update_pipeline()            
            
