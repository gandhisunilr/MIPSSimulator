import unittest
from Unit import *

class Tests(unittest.TestCase):
    def setUp(self):
        pass

class Pipeline:
    #get all parameters from file and initialize particular pipeline
    def __init__(self):
        pass

    def update_pipeline():
        IF = Unit('IF',1,True)
        IF.add_new_inst('GG: L.D F1, 4(R4)',0)
        EXADD = Unit('EXADD',6,True)
        for i in range(1,11):
            print "-------------"+str(i)+"--------------"
        #Find whether there is instruction in last stage
            print IF
            print EXADD
            last_stage_instruction = EXADD.last_stage.instruction
            EXADD.update_unit(i)
            if(EXADD.is_last_stage_free() and last_stage_instruction!=None):
                print last_stage_instruction.operation+" completed at "+str(i)
                if(EXADD.is_free() and not IF.is_free()):
                    EXADD.add_inst(IF,i)
                    IF.update_unit(i)
