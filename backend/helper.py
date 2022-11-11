import sys
import requests

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

def api_call(ipv4, type, commend, params=None):
    '''
    This function is used to use the api. \n
    The flag will need to be updated in the future to accommodate different api's.
    '''
    request_url = "http://{}".format(ipv4)
    url = request_url+commend
    print(" - Backend.helper.api_call: ", url)
    if type == "GET":
        return requests.get(url, params, timeout=0.5)
    elif type == "POST":
        return requests.post(url, params, timeout=0.5)