import sys

def byteSize(memcache:dict):
    '''
    This function return the size of the memcache.
    '''
    size = sys.getsizeof(memcache)
    keys = memcache.keys()
    values = memcache.values()
    #get size of all keys
    for key in keys:
        size = size + sys.getsizeof(key)
    #get size of all values
    for value in values:
        size = size + sys.getsizeof(value)
    return size

def mbytesize(memcache):
    return byteSize(memcache)/(1024*1024)

def checkSize(memcache,config_size):
    '''
    This function checks whether the size of memcache. If the size is greater than config_size, then return true,
    else return false.
    '''
    result = False
    size = mbytesize(memcache)
    if size > config_size:
        return result
    else:
        result = True
        return result

def mbytesize_obj(obj):
    return sys.getsizeof(obj)/(1024*1024)


    
    