from CacheBlock import *

class ICache:

    cache_size = 4
    cache_block_size = 4
    cache_block = []
    request_count = 0
    hit_count = 0

    def __init__(self,ICache_cycles,Mem_cycles):
        self.ICache_cycles = ICache_cycles
        self.Mem_cycles = Mem_cycles
        for i in range(self.cache_size):
            self.cache_block.append(CacheBlock(i,self.cache_block_size))

    def read(self, address):
        self.request_count += 1
        # print "ICache request "+str(address/4)+":"+str(self.request_count)
        tag = address >> 6
        blk_no = (address >> 4) % 4
        if self.cache_block[blk_no].valid == True and self.cache_block[blk_no].tag == tag:
            self.hit_count += 1
            return True, self.ICache_cycles
        else:
            self.cache_block[blk_no].tag = tag
            self.cache_block[blk_no].valid = True
            return False, (self.ICache_cycles + self.Mem_cycles) * 2

    def is_hit(self, address):
        # print "ICache check "+str(address/4)+":"+str(self.request_count)
        tag = address >> 6
        blk_no = (address >> 4) % 4
        if self.cache_block[blk_no].valid == True and self.cache_block[blk_no].tag == tag:
            return True, self.ICache_cycles
        else:
            return False, (self.ICache_cycles + self.Mem_cycles) * 2
