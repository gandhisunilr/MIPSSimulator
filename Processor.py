import unittest
import Instruction

class Tests(unittest.TestCase):
    def setUp(self):
        pass

class Unit():
    def __init__(self,name,number_of_stages,is_pipelined):
        self.name = name
        self.number_of_stages = number_of_stages
        self.is_pipelined= is_pipelined
        
class Stage():
    def __init__(self,instruction,stage_no,number_of_cycles,start):
        self.instruction = instruction
        self.stage_no = stage_no
        self.number_of_cycles = number_of_cycles
        self.start = start
        
        
        
        
        
        
        

