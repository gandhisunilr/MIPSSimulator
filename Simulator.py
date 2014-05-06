from Unit import *
from Instruction import *
from ICache import *
from DCache import *
import sys

class Pipeline:
    #get all parameters from file and initialize particular pipeline
    def __init__(self, file_inst, file_data, file_reg, file_config, file_result):
        self.read_files(file_inst, file_data, file_reg, file_config)
        self.file_result = file_result
        self.all_inst_fetched = False
        self.current_inst = 0
        self.result = dict()
        self.register_status = dict()
        self.flush = False
        self.inst_exec_list = {}
        self.IBUS = 'FREE'
        self.DBUS = 'FREE'

        # Create All Units
        self.IF = Unit('IF',1,False)
        self.ID = Unit('ID',1,True)
        self.EXMULT = Unit('EXMULT',self.EXMULT_cycles,self.EXMULT_pipelined)
        self.EXADD = Unit('EXADD',self.EXADD_cycles,self.EXADD_pipelined)
        self.EXDIV = Unit('EXDIV',self.EXDIV_cycles,self.EXDIV_pipelined)
        self.EXIU = Unit('EXIU',1,True)
        self.EXMEM = Unit('EXMEM',self.EXINT_cycles,False)
        self.WB = Unit('WB',1,True)

        self.icache = ICache(self.ICache_cycles,self.EXINT_cycles)
        
        self.dcache = DCache(256,self.data,self.DCache_cycles,self.EXINT_cycles)
        self.dbus_access = 0
        self.bus_contention = False

    def __repr__(self):
        pipeline_state = ""
        for i in range(len(self.inst_exec_list.keys())):
            pipeline_state += '{0: <24}'.format( self.inst_exec_list[i].upper().strip())+"\t"
            pipeline_state += str(self.result[i][0]) + '\t'
            pipeline_state += str(self.result[i][1]) + '\t'
            pipeline_state += str(self.result[i][2]) + '\t'
            pipeline_state += str(self.result[i][3]) + '\t'
            if self.result[i][4]==0:
                pipeline_state += ' N\t'
            else:
                pipeline_state += ' Y\t'
            if self.result[i][5]==0:
                pipeline_state += ' N\t'
            else:
                pipeline_state += ' Y\t'
            if self.result[i][6]==0:
                pipeline_state += ' N\t'
            else:
                pipeline_state += ' Y\t'
            if self.result[i][7]==0:
                pipeline_state += ' N\t'
            else:
                pipeline_state += ' Y\t'
            
            pipeline_state += '\n'
        
        return pipeline_state

    def __str__(self):
        pipeline_state=""
        pipeline_state += self.IF.__str__()+"\n"
        pipeline_state += self.ID.__str__()+"\n"
        pipeline_state += self.EXIU.__str__()+"\n"
        pipeline_state += self.EXMEM.__str__()+"\n"
        pipeline_state += self.EXADD.__str__()+"\n"
        pipeline_state += self.EXMULT.__str__()+"\n"
        pipeline_state += self.EXDIV.__str__()+"\n"
        pipeline_state += self.WB.__str__()+"\n"
        return pipeline_state

    def read_files(self,file_inst, file_data, file_reg, file_config):
        # Read all instructions
        f = open(file_inst)
        self.set_of_instructions = f.readlines()
        f.close()
        
        # Read config file
        f = open(file_config)
        lines = f.readlines()
        EXADD_params = lines[0].split(':')[1].strip()
        EXMULT_params = lines[1].split(':')[1].strip()
        EXDIV_params = lines[2].split(':')[1].strip()
        EXINT_params = lines[3].split(':')[1].strip()
        ICache_params = lines[4].split(':')[1].strip()
        DCache_params = lines[5].split(':')[1].strip()

        self.EXADD_cycles = int(EXADD_params.split(',')[0].strip(','))
        self.EXADD_pipelined = EXADD_params.split(',')[1].upper()=='YES'
        
        self.EXMULT_cycles = int(EXMULT_params.split(',')[0].strip(','))
        self.EXMULT_pipelined = EXMULT_params.split(',')[1].upper()=='YES'
        
        self.EXDIV_cycles = int(EXDIV_params.split(',')[0].strip(','))
        self.EXDIV_pipelined = EXDIV_params.split(',')[1].upper()=='YES'
        
        self.EXINT_cycles = int(EXINT_params.split()[0].strip(','))

        self.ICache_cycles = int(ICache_params.split()[0].strip(','))
        
        self.DCache_cycles = int(DCache_params.split()[0].strip(','))

        f.close()

        # Read register file
        file = open(file_reg, 'r')
        regs_string = file.readlines()
        self.registers = {'R'+str(i):int(regs_string[i].strip(),2) for i in range(len(regs_string))}
        self.registers['PC']=0
        
        # Read data file
        self.word_size = 4
        self.base_address = 256
        file = open(file_data, 'r')
        data_string = file.readlines()
        self.data = {self.base_address+(i*self.word_size):int(data_string[i].strip(),2) for i in range(len(data_string))}

    def update_pipeline(self):
        print self.registers
        first_instruction = Instruction(self.set_of_instructions[self.registers['PC']].strip(),self.current_inst)
        
        cache_hit ,fetch_stall_cycles = self.icache.read(self.registers['PC']*4)
        self.move_inst_unit_unpipelined(self.IF,None,fetch_stall_cycles)
        
        print "-------------0--------------"
        print self.__repr__()
        
        i = 1
        while(1):
            if(self.WB.is_free() and self.EXADD.is_free() and self.EXMULT.is_free() and self.EXDIV.is_free() and self.EXMEM.is_free() and self.EXIU.is_free() and self.all_inst_fetched):
                break

            print "-------------"+str(i)+"--------------"
            self.WB.execute_unit()
            self.complete_execution(self.WB.get_completed_inst(),'WB',i)

            self.EXADD.execute_unit()
            self.EXMULT.execute_unit()
            self.EXDIV.execute_unit()
            
            if(not self.bus_contention):
                self.EXMEM.execute_unit()
            else:
                if(self.IBUS=='FREE'):
                    self.DBUS = 'BUSY'
                    self.EXMEM.execute_unit()
                
            WB_inst_candidates = []
            WB_inst_candidates.append(self.EXADD.peek_completed_inst())
            WB_inst_candidates.append(self.EXMULT.peek_completed_inst())
            WB_inst_candidates.append(self.EXDIV.peek_completed_inst())
            WB_inst_candidates.append(self.EXMEM.peek_completed_inst())
            WB_unit_candidates = [self.EXADD,self.EXMULT,self.EXDIV,self.EXMEM]
            prioritized_unit = self.get_prioritized_unit(WB_inst_candidates,WB_unit_candidates)
            
            if(prioritized_unit == self.EXADD):
                self.complete_execution(self.move_inst_unit(self.WB,self.EXADD),'EXADD',i)
            elif(prioritized_unit == self.EXMULT):
                self.complete_execution(self.move_inst_unit(self.WB,self.EXMULT),'EXMULT',i)
            elif(prioritized_unit == self.EXDIV):
                self.complete_execution(self.move_inst_unit(self.WB,self.EXDIV),'EXDIV',i)
            elif(prioritized_unit == self.EXMEM):
                self.complete_execution(self.move_inst_unit(self.WB,self.EXMEM),'EXMEM',i)

            self.EXIU.execute_unit()
            EXIU_inst =  self.EXIU.peek_completed_inst()
            if(EXIU_inst!= False):
                if(EXIU_inst.operation in ['LW', 'SW', 'L.D', 'S.D'] ):
                    if(self.EXMEM.is_free()):
                        first_word_time,second_word_time = self._calc_memory_cycles(EXIU_inst)
                        if(self.first_word_hit and self.second_word_hit):
                            self.complete_execution(self.move_inst_unit_unpipelined(self.EXMEM,self.EXIU,first_word_time+second_word_time),'EXIU',i)
                        else:
                            if(self.IBUS=='FREE'):
                                self.DBUS = 'BUSY'
                                self.dbus_access = i
                                self.complete_execution(self.move_inst_unit_unpipelined(self.EXMEM,self.EXIU,first_word_time+second_word_time),'EXIU',i)

                    else:
                        self.result[EXIU_inst.inst_addr][7] = 'Y'
                else:
                    self.complete_execution(self.move_inst_unit_unpipelined(self.EXMEM,self.EXIU,1),'EXIU',i)

            self.ID.execute_unit()
            ID_inst =  self.ID.peek_completed_inst()
            if(not self.hazards(ID_inst)):
                if(ID_inst!= False):
                    if(ID_inst.exunit == 'EXADD'):
                        self.complete_execution(self.move_inst_unit(self.EXADD,self.ID),'ID',i)
                    elif(ID_inst.exunit == 'EXMULT'):
                        self.complete_execution(self.move_inst_unit(self.EXMULT,self.ID),'ID',i)
                    elif(ID_inst.exunit == 'EXDIV'):
                        self.complete_execution(self.move_inst_unit(self.EXDIV,self.ID),'ID',i)
                    elif(ID_inst.exunit == 'EXINT'):
                        self.complete_execution(self.move_inst_unit(self.EXIU,self.ID),'ID',i)
                    elif(ID_inst.exunit == 'None'):
                        self.handle_decode_inst(self.ID.get_completed_inst(),i)

            self.IF.execute_unit()
            if(self.flush):
                IF_inst = self.IF.get_completed_inst()
                if(IF_inst!=False):
                    if IF_inst.inst_addr not in self.result.keys():
                        self.result[IF_inst.inst_addr] = [0]*8
                        self.inst_exec_list[IF_inst.inst_addr] = IF_inst.instruction_str
                    self.result[IF_inst.inst_addr][0] = i
                self.flush = False
            else:
                self.complete_execution(self.move_inst_unit(self.ID,self.IF),'IF',i)

            if(self.IF.is_free()):
                cache_hit ,fetch_stall_cycles = self.icache.read(self.registers['PC']*4)
                if(cache_hit):
                    self.move_inst_unit_unpipelined(self.IF,None,fetch_stall_cycles)
                else:
                    if(self.DBUS=='FREE'):
                        self.move_inst_unit_unpipelined(self.IF,None,fetch_stall_cycles)
                        self.IBUS = 'BUSY'
                    else:
                        if(self.dbus_access==i):
                            self.move_inst_unit_unpipelined(self.IF,None,fetch_stall_cycles)
                            self.IBUS = 'BUSY'
                            self.DBUS = 'FREE'
                            self.bus_contention = True
                        else:
                            pass # STALL or do not move in IF stage

            # print self.__repr__()
            # print self
            i +=1

        # print self.__repr__()
        # print self.registers

    def handle_decode_inst(self,instruction,clk):
        self.result[instruction.inst_addr][1] = clk
        if(instruction.operation=='HLT'):
            self.all_inst_fetched = True
            self.flush = True

        elif instruction.operation == 'J':
            self.registers['PC'] = self._get_corresponding_inst(instruction.op1)
            self.all_inst_fetched = False
            self.flush = True

        elif instruction.operation == 'BEQ':
            if self.registers[instruction.dest] == self.registers[instruction.op1]:
                self.registers['PC'] = self._get_corresponding_inst(instruction.op2)
                self.all_inst_fetched = False
                self.flush = True

        elif instruction.operation == 'BNE':
            if self.registers[instruction.dest] != self.registers[instruction.op1]:
                self.registers['PC'] = self._get_corresponding_inst(instruction.op2)
                self.all_inst_fetched = False
                self.flush = True

    def _get_corresponding_inst(self,label):
        for i in range(len(self.set_of_instructions)):
            instruction = Instruction(self.set_of_instructions[i],i)
            if instruction.label==label:
                return i


    def move_inst_unit(self,to_unit,from_unit):
        if(to_unit.is_free()):
            if(from_unit==None):
                if(self.all_inst_fetched==False):
                    from_unit_complete_inst = Instruction(self.set_of_instructions[self.registers['PC']].strip(),self.current_inst)
                    self.registers['PC'] +=1
                    self.current_inst +=1
                else:
                        return
            else:
                from_unit_complete_inst =from_unit.get_completed_inst()
            if(from_unit_complete_inst!=False):
                if(to_unit.add_new_inst(from_unit_complete_inst)==False):
                    print "Debugging Time"
                    return False
            return from_unit_complete_inst
        else:
            if(from_unit!=None and from_unit!=self.IF):
                if(from_unit.peek_completed_inst()!=False):
                    self.result[from_unit.peek_completed_inst().inst_addr][7] = 'Y'
            return False

    def move_inst_unit_unpipelined(self,to_unit,from_unit,number_of_cycles):
        if(to_unit.is_free()):
            if(from_unit==None):
                if(self.all_inst_fetched==False):
                    from_unit_complete_inst = Instruction(self.set_of_instructions[self.registers['PC']].strip(),self.current_inst)
                    self.registers['PC'] +=1
                    self.current_inst +=1
                else:
                        return
            else:
                from_unit_complete_inst =from_unit.get_completed_inst()
            if(from_unit_complete_inst!=False):
                if(to_unit.add_new_inst_unpipelined(from_unit_complete_inst,number_of_cycles)==False):
                    print "Debugging Time"
                    return False
            return from_unit_complete_inst
        else:
            if(from_unit!=None and from_unit!=self.IF):
                if(from_unit.peek_completed_inst()!=False):
                    self.result[from_unit.peek_completed_inst().inst_addr][7] = 'Y'
            return False

    def __max_priority(self,inst_list,unit_list,insts_start):
        if(len(inst_list)==0):
            return None
        priority = [0]*len(unit_list)
        for i in range(len(unit_list)):
            priority[i] += unit_list[i].number_of_cycles*10
            priority[i] -= insts_start[i]
            if(not unit_list[i].is_pipelined and unit_list[i]!=self.EXMEM):
                priority[i] += 32768
        return unit_list[priority.index(max(priority))]
            
    def get_prioritized_unit(self,WB_inst_candidates,WB_unit_candidates):
        WB_inst_final_candidates = []
        WB_unit_final_candidates = []
        insts_start = []
        for i in range(len(WB_inst_candidates)):
            if( WB_inst_candidates[i] != False):
                WB_inst_final_candidates.append(WB_inst_candidates[i])
                WB_unit_final_candidates.append(WB_unit_candidates[i])
                insts_start.append(WB_inst_candidates[i].inst_addr)
        winning_unit=self.__max_priority(WB_inst_final_candidates,WB_unit_final_candidates,insts_start)
        for i in range(len(WB_inst_final_candidates)):
            if(WB_unit_final_candidates[i]!=winning_unit):
                self.result[WB_inst_final_candidates[i].inst_addr][7]='Y'
        return winning_unit
    
    def complete_execution(self,instruction,execution_unit,clk):
        if(instruction!=False):
            if instruction.inst_addr not in self.result.keys():
                self.result[instruction.inst_addr] = [0]*8
                self.inst_exec_list[instruction.inst_addr] = instruction.instruction_str
            if(execution_unit=='WB'):
                print instruction.operation+" is completed"
                self.result[instruction.inst_addr][3] = clk
                self.register_status[instruction.dest]='FREE'
            elif(execution_unit in ['EXADD','EXMULT','EXDIV','EXMEM']):
                self._execute(instruction)
                self.result[instruction.inst_addr][2] = clk
                # Execute the instruction here
                if(execution_unit=='EXMEM'):
                    self.DBUS = 'FREE'
                    self.bus_contention = False
            elif(execution_unit=='ID'):
                self.result[instruction.inst_addr][1] = clk
                self.register_status[instruction.dest]='BUSY'
                self.IBUS ='FREE'
            elif(execution_unit=='IF'):
                self.result[instruction.inst_addr][0] = clk

    def hazards(self,instruction):
        if(instruction!= False):
            if(instruction.op1 in self.register_status):
                if(self.register_status[instruction.op1]=='BUSY'):
                    self.result[instruction.inst_addr][4] = 'Y'
                    return True
            if(instruction.op2 in self.register_status):
                if(self.register_status[instruction.op2]=='BUSY'):
                    self.result[instruction.inst_addr][4] = 'Y'
                    return True
            if(instruction.dest in self.register_status):
                if(self.register_status[instruction.dest]=='BUSY'):
                    self.result[instruction.inst_addr][6] = 'Y'
                    return True
        return False

    def _execute(self,instruction):
        if(instruction.operation == 'DADD'):
            self.registers[instruction.dest] = self.registers[instruction.op1] + self.registers[instruction.op2]

        elif instruction.operation == 'DADDI':
            self.registers[instruction.dest] = self.registers[instruction.op1] + int(instruction.op2)

        elif instruction.operation == 'DSUB':
            self.registers[instruction.dest] = self.registers[instruction.op1] - self.registers[instruction.op2]

        elif instruction.operation == 'DSUBI':
            self.registers[instruction.dest] = self.registers[instruction.op1] - int(instruction.op2)

        elif instruction.operation == 'AND':
            self.registers[instruction.dest] = self.registers[instruction.op1] & self.registers[instruction.op2]

        elif instruction.operation == 'ANDI':
            self.registers[instruction.dest] = self.registers[instruction.op1] & int(instruction.op2)

        elif instruction.operation == 'OR':
            self.registers[instruction.dest] = self.registers[instruction.op1] | self.registers[instruction.op2]

        elif instruction.operation == 'ORI':
            self.registers[instruction.dest] = self.registers[instruction.op1] | int(instruction.op2)

    def _calc_memory_cycles(self,instruction):
        if instruction.operation == 'LW':
            offset = instruction.op1.split('(')[0].strip()
            address = int(offset) + self.registers[instruction.op1.split('(')[1].strip(')')]
            self.first_word_hit, self.registers[instruction.dest], cycles = self.dcache.read(address)
            return cycles, 0

        elif instruction.operation == 'L.D':
            offset = instruction.op1.split('(')[0].strip()
            address = int(offset) + self.registers[instruction.op1.split('(')[1].strip(')')]
            self.first_word_hit, word, first_word_read_time = self.dcache.read(address)
            self.second_word_hit, word, second_word_read_time = self.dcache.read(address + 4)
            return first_word_read_time, second_word_read_time

        elif instruction.operation == 'SW':
            offset = instruction.op1.split('(')[0].strip()
            address = int(offset) + self.registers[instruction.op1.split('(')[1].strip(')')]
            self.first_word_hit, cycles = self.dcache.write(address, self.registers[instruction.src_reg[0]])
            return cycles, 0

        elif instruction.operation == 'S.D':
            offset = instruction.op1.split('(')[0].strip()
            address = int(offset) + self.registers[instruction.op1.split('(')[1].strip(')')]
            self.first_word_hit, first_word_write_time = self.dcache.write(address, 0, False)
            self.second_word_hit, second_word_write_time = self.dcache.write(address + 4, 0, False)
            return first_word_write_time, second_word_write_time

        return 1, 0

    def print_result(self):

        output = ''
        output += '-' * 94 + '\n'
        output += '\tInstruction\t\tFT\tID\tEX\tWB\tRAW\tWAR\tWAW\tStruct\n'
        output += '-' * 94 + '\n'

        output += self.__repr__()

        output += '-' * 94 + '\n'
        output += '\nTotal number of access requests for instruction cache: ' + str(self.icache.request_count)
        output += '\nNumber of instruction cache hits: ' + str(self.icache.hit_count)
        output += '\nTotal number of access requests for data cache: ' + str(self.dcache.request_count)
        output += '\nNumber of data cache hits: ' + str(self.dcache.hit_count)

        file = open(self.file_result, 'w')
        file.write(output)
        file.close()
        print output

if __name__ == '__main__':
    if len(sys.argv) != 6:
        print('Usage: python Simulator.py inst.txt data.txt reg.txt config.txt result.txt')
        exit()
    p1 = Pipeline(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5])
    p1.update_pipeline()
    p1.print_result()

