import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ctypes import *
from enum import Enum

from cachecow.Cache.LRU import LRU
from cachecow.CacheReader.basicCacheReader import basicCacheReader
from cachecow.Profiler.abstract.getMRCAbstractLRU import getMRCAbstractLRU


class parda_mode(Enum):
    seq = 1
    openmp = 2
    mpi = 3
    hybrid = 4



class parda(getMRCAbstractLRU):
    def __init__(self, cache_class, cache_size, reader, bin_size=1):
        super().__init__(cache_class, cache_size, bin_size, reader)

        # load the shared object file
        self.parda_seq = CDLL(os.path.join(os.path.dirname(__file__), self.get_lib_name()))

        self.c_float_array = (c_float * (self.cache_size + 1))()
        self.c_cache_size = c_long(self.cache_size)


        # if the given file is not basic reader, needs conversion
        if not isinstance(reader, basicCacheReader):
            self.prepare_file()

        self.num_of_lines = self.reader.get_num_total_lines()
        print("lines: %d" % self.num_of_lines)


    def get_lib_name(self):
        for name in os.listdir(os.path.dirname(os.path.abspath(__file__))):
            if 'libparda' in name and '.py' not in name:
                return name 


    def prepare_file(self):
        print("changing file format")
        with open('temp.dat', 'w') as ofile:
            for i in self.reader:
                ofile.write(str(i) + '\n')
        self.reader = basicCacheReader('temp.dat')



    def addOneTraceElement(self, element):
        # do not need this function in this profiler
        pass

    def run(self, mode, *args, **kargs):
        c_line_num = c_long(self.num_of_lines)
        c_file_name = c_char_p(self.reader.file_loc.encode())

        if mode == parda_mode.seq:
            self.mode = mode
            c_begin = c_long(40000)
            c_end = c_long(self.num_of_lines - 40000)
            self.parda_seq.classical_tree_based_stackdist(c_file_name, c_line_num, self.c_cache_size,
                                                          self.c_float_array)

        elif mode == parda_mode.openmp:
            self.num_of_threads = kargs["threads"]
            self.mode = mode
            c_threads = c_int(self.num_of_threads)
            self.parda_seq.parda_seperate_file(c_file_name, c_threads, c_line_num)
            print("all files have been separated for parallel")
            # self.parda_seq.parda_omp_stackdist.restype = POINTER(c_double)
            self.parda_seq.parda_omp_stackdist(c_file_name, c_line_num, c_threads, self.c_cache_size,
                                               self.c_float_array)

        elif mode == parda_mode.mpi:
            print('sorry, currently, mpi mode is not supported')
        elif mode == parda_mode.hybrid:
            print('sorry, currently, openmp/mpi hybrid mode is not supported')
        else:
            print("does not support given run mode")

        self.run_aux()

    def run_with_specified_lines(self, begin_line, end_line):
        c_line_num = c_long(self.num_of_lines)
        c_file_name = c_char_p(self.reader.file_loc.encode())

        c_begin = c_long(begin_line)
        c_end = c_long(end_line)
        self.parda_seq.classical_with_line_specification(c_file_name, c_line_num, self.c_cache_size,
                                                         c_begin, c_end, self.c_float_array)
        self.run_aux()

    def run_aux(self):
        self.calculated = True

        for i in range(self.cache_size):
            self.HRC_bin[i] = self.c_float_array[i + 1] * 100

        self.HRC[0] = self.HRC_bin[0]
        for i in range(1, self.cache_size):
            self.HRC[i] = self.HRC_bin[i] + self.HRC[i - 1]

        # the size of list is one larger than cache_size, if bin_size is 1
        self.HRC[-1] = self.HRC[-2]

        for i in range(self.num_of_blocks):
            self.MRC[i] = 100 - self.HRC[i]

        for i in range(len(self.MRC)):
            pass

    def __del__(self):
        if os.path.exists('temp.dat'):
            os.remove('temp.dat')


if __name__ == "__main__":
    p = parda(LRU, 30000, basicCacheReader("../Data/parda.trace"))
    # p.run(parda_mode.seq, threads=4)
    p.run_with_specified_lines(10000, 120000)
    p.plotHRC(autosize=True, autosize_threshhold=0.001)
