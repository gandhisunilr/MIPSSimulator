import unittest
from Instruction import *

class Tests(unittest.TestCase):
    def setUp(self):
        self.s1 = Stage(Instruction('GG: L.D F1, 4(R4)'),0,1,1)
        self.s2 = Stage(Instruction('GG: L.D F1, 4(R4)'),1,1,1)
        self.s3 = Stage(Instruction('ADD.D F4, F6, F2'),2,1,1)
        self.s4 = Stage(None,3,1,None)

    def test_is_free(self):
        self.assertEquals(self.s1.is_free(),0)
        
    def test_update_stage(self):
        self.s2.update_stage(2)
        self.assertEquals(self.s2.is_free(),1)
        
    def test_add_inst(self):
        self.s3.update_stage(2)
        self.assertEquals(self.s3.is_free(),1)
        self.s3.add_inst(self.s2,2)
        self.assertEquals(self.s3.is_free(),0)
        self.s4.add_new_inst(Instruction('ADD.D F4, F6, F2'),1)
        self.assertEquals(self.s3.is_free(),0)

class Stage():
    def __init__(self,instruction,stage_no,number_of_cycles,start):
        self.instruction = instruction
        self.stage_no = stage_no
        self.number_of_cycles = number_of_cycles
        self.start = start
    
    def is_free(self):
        if(self.instruction==None):
            return 1
        else:
            return 0
    
    def update_stage(self,clk):
        if(self.start == None):
            return
        if((self.start+self.number_of_cycles)==clk):
            self.instruction = None
            self.start = None
        
    def add_inst(self,prev_stage,clk):
        if(self.instruction==None):
            self.instruction = prev_stage.instruction
            self.start= clk
        else:
            print "cannot move from"+prev_stage.stage_no
            print self.stage_no+ "is not free"

    def  add_new_inst(self,instruction,clk):
        if(self.instruction==None):
            self.instruction = instruction
            self.start= clk
        else:
            print "cannot add new instruction"+instruction.operation
            print self.stage_no+ "is not free"

    def __str__(self):
        stage_state = str(self.stage_no)
        if(self.instruction!=None):
            stage_state += ":"+self.instruction.operation
            stage_state += " Start: "+str(self.start )
        else:
            stage_state += ":None"
        return stage_state+"\n"

if __name__ == '__main__':
    unittest.main()
