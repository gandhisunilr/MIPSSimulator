import unittest
from Instruction import *

class Tests(unittest.TestCase):
    def setUp(self):
        self.s1 = Stage(Instruction('GG: L.D F1, 4(R4)'),0,1,1)
        self.s2 = Stage(Instruction('GG: L.D F1, 4(R4)'),1,1,1)
        
    def test_is_free(self):
        self.assertEquals(self.s1.is_free(),0)
        
    def test_update_stage(self):
        self.s2.update_stage(2)
        self.assertEquals(self.s2.is_free(),1)
        
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
        if(self.start+self.number_of_cycles==clk):
            self.instruction = None
        

if __name__ == '__main__':
    unittest.main()
