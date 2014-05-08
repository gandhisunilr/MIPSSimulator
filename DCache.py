from CacheBlock import *
from CacheSet import *

class DCache:

    word_size = 4
    cache_size = 4
    cache_sets = 2
    cache_block_size = 4
    sets = []
    request_count = 0
    hit_count = 0
    lru_for_cache_block = [0, 0]

    def __init__(self,memory_base_address,data,DCache_cycles,Mem_cycles):
        self.data = data
        self.memory_base_address = memory_base_address
        self.DCache_cycles = DCache_cycles
        self.Mem_cycles = Mem_cycles

        for i in range(self.cache_sets):
            self.sets.append(CacheSet(i, self.cache_size / self.cache_sets))
    
    def read(self, address):
        self.request_count += 1
        address -= self.memory_base_address
        blk_no = (address >> 4) % 2
        read_cycles = 0

        for i in range(self.cache_sets):
            if self._is_address_present_in_set(address, i):
                self.hit_count += 1
                self._set_lru(blk_no, i)
                return True, self.sets[i].cache_block[blk_no].words[(address & 12) >> 2], self.DCache_cycles

        set_no = DCache.lru_for_cache_block[blk_no]

        if DCache.sets[set_no].cache_block[blk_no].dirty:
            read_cycles += DCache._write_back(set_no, blk_no)

        self._setup_block(address, set_no)
        read_cycles += (self.DCache_cycles + self.Mem_cycles) * 2
        return False, DCache.sets[set_no].cache_block[blk_no].words[(address & 12) >> 2], read_cycles


    def write(self, address, value, writable = True):
        self.request_count += 1
        address -= self.memory_base_address
        blk_no = (address >> 4) % 2
        write_cycles = 0

        for i in range(self.cache_sets):
            if self._is_address_present_in_set(address, i):
                self.hit_count += 1
                self._set_lru(blk_no, i)
                self._set_value(address, i, value, writable)
                return True, self.DCache_cycles

        set_no = self.lru_for_cache_block[blk_no]

        if self.sets[set_no].cache_block[blk_no].dirty:
            write_cycles += self._write_back(set_no, blk_no)

        self._setup_block(address, set_no)
        self._set_value(address, set_no, value, writable)
        return False, write_cycles + (self.DCache_cycles + self.Mem_cycles) * 2


    def is_hit(self, address):
        address -= self.memory_base_address
        for i in range(self.cache_sets):
            if DCache._is_address_present_in_set(address, i):
                return True
        return False


    def _is_address_present_in_set(self, address, set_no):
        tag = address >> 5
        blk_no = (address >> 4) % 2
        return DCache.sets[set_no].is_block_valid(blk_no) and DCache.sets[set_no].tag_for_block(blk_no) == tag


    def _write_back(self, set_no, blk_no):
        tag = DCache.sets[set_no].cache_block[blk_no].tag
        base_address = self.memory_base_address + ((tag << 5) | (blk_no << 4))
        for i in range(CACHE_BLOCK_SIZE):
            self.data[base_address + (i * self.word_size)] = DCache.sets[set_no].cache_block[blk_no].words[i]
        return (self.DCache_cycles + self.Mem_cycles) * 2

    def _setup_block(self, address, set_no):
        blk_no = (address >> 4) % 2
        DCache.sets[set_no].cache_block[blk_no].tag = address >> 5
        DCache.sets[set_no].cache_block[blk_no].valid = True
        self._set_lru(blk_no, set_no)
        self._read_from_memory(address, set_no)

    def _set_lru(self, blk_no, set_no):
        DCache.lru_for_cache_block[blk_no] = 1 if set_no == 0 else 0

    def _read_from_memory(self, address, set_no):
        blk_no = (address >> 4) % 2
        base_address = self.memory_base_address + ((address >> 4) << 4)
        for i in range(self.cache_block_size):
            DCache.sets[set_no].cache_block[blk_no].words[i] = self.data[base_address + (i * self.word_size)]

    def _set_value(self, address, set_no, value, writable):
        blk_no = (address >> 4) % 2
        DCache.sets[set_no].cache_block[blk_no].dirty = True
        if writable:
            DCache.sets[set_no].cache_block[blk_no].words[(address & 12) >> 2] = value
