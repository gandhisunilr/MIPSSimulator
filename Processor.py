from Unit import *
from Instruction import *

class Pipeline:
    #get all parameters from file and initialize particular pipeline
    def __init__(self):
        self.read_files()
        self.all_inst_fetched = False
        self.current_inst = 0

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
        EXINT_params = lines[3].split(':')[1].strip()

        self.EXADD_cycles = int(EXADD_params.split()[0].strip(','))
        self.EXADD_pipelined = EXADD_params.split()[1].upper()=='YES'
        
        self.EXMULT_cycles = int(EXMULT_params.split()[0].strip(','))
        self.EXMULT_pipelined = EXMULT_params.split()[1].upper()=='YES'
        
        self.EXDIV_cycles = int(EXDIV_params.split()[0].strip(','))
        self.EXDIV_pipelined = EXDIV_params.split()[1].upper()=='YES'
        
        self.EXINT_cycles = int(EXINT_params.split()[0].strip(','))
        self.EXINT_pipelined = EXINT_params.split()[1].upper()=='YES'
        
        f.close()

    def update_pipeline(self):        
        first_instruction = Instruction(self.set_of_instructions[self.current_inst].strip())
        self.IF.add_new_inst(first_instruction)
        self.current_inst +=1
        print "-------------1--------------"
        print self
        
        for i in range(2,20):
            print "-------------"+str(i)+"--------------"
            self.WB.execute_unit()
            self.WB.remove_all_completed()

            WB_inst_candidates = []
            self.EXADD.execute_unit()
            WB_inst_candidates.append(self.EXADD.peek_completed_inst())
            self.EXMULT.execute_unit()
            WB_inst_candidates.append(self.EXMULT.peek_completed_inst())
            self.EXDIV.execute_unit()
            WB_inst_candidates.append(self.EXDIV.peek_completed_inst())
            WB_unit_candidates = [self.EXADD,self.EXMULT,self.EXDIV]
            prioritized_unit = self.get_prioritized_unit(WB_inst_candidates,WB_unit_candidates)
            
            if(prioritized_unit == self.EXADD):
                self.move_inst_unit(self.WB,self.EXADD)
            elif(prioritized_unit == self.EXMULT):
                self.move_inst_unit(self.WB,self.EXMULT)
            elif(prioritized_unit == self.EXDIV):
                self.move_inst_unit(self.WB,self.EXDIV)

            self.ID.execute_unit()
            ID_inst =  self.ID.peek_completed_inst()
            if(ID_inst!= False):
                if(ID_inst.exunit == 'EXADD'):
                    self.move_inst_unit(self.EXADD,self.ID)
                elif(ID_inst.exunit == 'EXMULT'):
                    self.move_inst_unit(self.EXMULT,self.ID)
                elif(ID_inst.exunit == 'EXDIV'):
                    self.move_inst_unit(self.EXDIV,self.ID)

            self.IF.execute_unit()
            self.move_inst_unit(self.ID,self.IF)
            
            self.move_inst_unit(self.IF,None)
            print self
            

    def move_inst_unit(self,to_unit,from_unit):
        if(to_unit.is_free()):
            if(from_unit==None):
                if(self.all_inst_fetched==False):
                    from_unit_complete_inst = Instruction(self.set_of_instructions[self.current_inst].strip())
                    self.current_inst +=1
                    if(from_unit_complete_inst.operation=='HLT'):
                        self.all_inst_fetched = True
                        return
                else:
                        return
            else:
                from_unit_complete_inst =from_unit.get_completed_inst()
            if(from_unit_complete_inst!=False):
                if(to_unit.add_new_inst(from_unit_complete_inst)==False):
                    print "Debugging Time"
    
    def __max_priority(self,inst_list,unit_list,insts_start):
        if(len(inst_list)==0):
            return None
        priority = [0]*len(unit_list)
        for i in range(len(unit_list)):
            priority[i] += unit_list[i].number_of_cycles*10
            priority[i] -= insts_start[i]
            if(not unit_list[i].is_pipelined):
                priority[i] += 32768
        return unit_list[priority.index(max(priority))]
            
    def get_prioritized_unit(self,WB_inst_candidates,WB_unit_candidates):
        set_of_inst_uppr = [instr.upper().strip() for instr in self.set_of_instructions]
        WB_inst_final_candidates = []
        WB_unit_final_candidates = []
        insts_start = []
        for i in range(len(WB_inst_candidates)):
            if( WB_inst_candidates[i] != False):
                WB_inst_final_candidates.append(WB_inst_candidates[i])
                WB_unit_final_candidates.append(WB_unit_candidates[i])
                insts_start.append(set_of_inst_uppr.index(WB_inst_candidates[i].instruction_str))

        return self.__max_priority(WB_inst_final_candidates,WB_unit_final_candidates,insts_start)

if __name__ == '__main__':
    #unittest.main()
    p1 = Pipeline()
    p1.update_pipeline()            
            
