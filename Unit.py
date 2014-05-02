import unittest
from collections import deque

class Unit():
    def __init__(self,name,number_of_cycles,is_pipelined):
        self.name = name
        self.number_of_cycles = number_of_cycles
        self.is_pipelined= is_pipelined
        self.number_of_inst = 0
        self.inst_queue = []
        self.completed_queue = deque()

    def __str__(self):
        str1 = self.name+"\n"
        for inst in self.inst_queue:
            str1 += inst[0].instruction_str+':'+str(inst[1])+"\n"
        for inst in self.completed_queue:
            str1 += inst[0].instruction_str+':'+str(inst[1])+"\n"
        return str1

    def add_new_inst(self,new_inst):
        if (self.is_pipelined):
            if self.number_of_inst==self.number_of_cycles:
                return False
            else:
                self.inst_queue.append((new_inst,self.number_of_cycles))
                self.number_of_inst +=1
        else:
            if self.number_of_inst==1:
                return False
            else:
                self.inst_queue.append((new_inst,self.number_of_cycles))
                self.number_of_inst +=1

    def execute_unit(self):
        updated_inst_queue = []
        for inst in self.inst_queue:
            updated_inst = (inst[0],inst[1]-1)
            if(updated_inst[1]==0):
                self.completed_queue.appendleft(updated_inst)
            else:
                updated_inst_queue.append(updated_inst)
        self.inst_queue = updated_inst_queue

    def remove_all_completed(self):
        for i in range(len(self.completed_queue)):
            print self.completed_queue.pop()[0].operation+" is completed"
            self.number_of_inst -=1
    
    def is_free(self):
        if (self.is_pipelined):
            if self.number_of_inst==self.number_of_cycles:
                return False
            else:
                return True
        else:
            if self.number_of_inst==1:
                return False
            else:
                return True
    
    def get_completed_inst(self):
        if(len(self.completed_queue)!=0):
            self.number_of_inst -= 1
            return self.completed_queue.pop()[0]
        else:
            return False
        
    def peek_completed_inst(self):
        if(len(self.completed_queue)!=0):
            return self.completed_queue[len(self.completed_queue)-1][0]
        else:
            return False
