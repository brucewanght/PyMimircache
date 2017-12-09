# coding=utf-8
"""
this module supposed to have some const,
but it is not well organized, the cache name mapping should be moved out of this file


"""

import os
import sys


CExtensionMode = True
INTERNAL_USE = True

DEFAULT_BIN_NUM_PROFILER = 100
DEFAULT_NUM_OF_THREADS = os.cpu_count()


failed_components = []
try:
    import mimircache.c_cacheReader
except Exception as e:
    print(e)
    failed_components.append("c_cacheReader")
try:
    import mimircache.c_LRUProfiler
except Exception as e:
    print(e)
    failed_components.append("c_LRUProfiler")
try:
    import mimircache.c_generalProfiler
except Exception as e:
    print(e)
    failed_components.append("c_generalProfiler")
try:
    import mimircache.c_heatmap
except Exception as e:
    print(e)
    failed_components.append("c_heatmap")

if len(failed_components):
    CExtensionMode = False
    print("C extension {} import failed, performance will degrade, "
          "if this is installation, you can ignore it".
            format(", ".join(failed_components)), file=sys.stderr)


from mimircache.cache.arc import ARC
from mimircache.cache.fifo import FIFO
from mimircache.cache.lru import LRU
from mimircache.cache.mru import MRU
from mimircache.cache.optimal import Optimal
from mimircache.cache.random import Random
from mimircache.cache.s4lru import S4LRU
from mimircache.cache.slru import SLRU
from mimircache.cache.clock import clock
try:
    from mimircache.cache.INTERNAL.ASig import ASig
except:
    ASig = None

from mimircache.cacheReader.csvReader import CsvReader
from mimircache.cacheReader.plainReader import PlainReader
from mimircache.cacheReader.vscsiReader import VscsiReader
from mimircache.cacheReader.binaryReader import BinaryReader

# global c_available_cache
c_available_cache = ["lru"
, "lfufast"
, "fifo"
, "optimal"
, "lru_k"
, "lru_2"
, "lfu"
, "mru"
, "random"
, "lrfu"
, "arc"
, "slru"
, "mimir"
, "amp"
, "pg "
, "slruml"
, "scoreml"
, "akamai"
]

c_available_cacheReader = [PlainReader, VscsiReader, CsvReader, BinaryReader]
cache_alg_mapping = {}


def init_cache_alg_mapping():
    """
    match all possible cache replacement algorithm names(lower case) to available cache replacement algorithms
    :return:
    """

    cache_alg_mapping['optimal'] = 'Optimal'
    cache_alg_mapping['opt'] = "Optimal"

    cache_alg_mapping['rr'] = "Random"
    cache_alg_mapping['random'] = "Random"

    cache_alg_mapping['lru'] = "LRU"

    cache_alg_mapping['mru'] = "MRU"

    cache_alg_mapping['lfu'] = "LFU"
    cache_alg_mapping['lfu_fast'] = "LFUFast"
    cache_alg_mapping['lfufast'] = "LFUFast"

    cache_alg_mapping['fifo'] = "FIFO"
    cache_alg_mapping['clock'] = "clock"

    cache_alg_mapping['arc'] = "ARC"

    cache_alg_mapping['lru_k'] = "LRU_K"
    cache_alg_mapping['lru_2'] = "LRU_2"


    cache_alg_mapping['slru'] = "SLRU"
    cache_alg_mapping['s4lru'] = "S4LRU"

    cache_alg_mapping['lrfu'] = "LRFU"
    cache_alg_mapping['slruml'] = "SLRUML"
    cache_alg_mapping['scoreml'] = "ScoreML"

    cache_alg_mapping["akamai"] = "akamai"
    cache_alg_mapping["new1"] = "new1"
    cache_alg_mapping["new2"] = "new2"


    cache_alg_mapping['mimir'] = 'mimir'
    cache_alg_mapping['amp'] = "AMP"
    cache_alg_mapping['pg'] = "PG"

    cache_alg_mapping["asig"] = "ASig"


def cache_name_to_class(name):
    """
    convert cache name to cache class
    :param name: name of cache
    :return:
    """
    cache_class = None
    if name.lower() in cache_alg_mapping:
        cache = cache_alg_mapping[name.lower()]
        if cache == 'Random':
            cache_class = Random
        elif cache == 'SLRU':
            cache_class = SLRU
        elif cache == 'S4LRU':
            cache_class = S4LRU
        elif cache == 'ARC':
            cache_class = ARC
        elif cache == 'LRU':
            cache_class = LRU
        elif cache == "Optimal":
            cache_class = Optimal
        elif cache == 'FIFO':
            cache_class = FIFO
        elif cache == "MRU":
            cache_class = MRU
        elif cache == 'clock':
            cache_class = clock
        elif cache == 'FIFO':
            cache_class = FIFO
        elif cache == "ASig":
            cache_class = ASig

    if cache_class:
        return cache_class
    else:
        raise RuntimeError("cannot recognize given cache replacement algorithm " + str(name))

