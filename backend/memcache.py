import random
from backend.helper import mbytesize, mbytesize_obj
# from backend.data import Data
# sql_connection = Data()

class Memcache:
    memcacheKeyValue = None
    memcacheKeyUploadTime = None
    memcacheKeyUsage = None            # Record memcacheKeyUsage of each key
    itemNum = None
    itemSize = None
    requestNum = None
    hit = None
    miss = None
    missRate = None
    hitRate = None
    configSize = None
    # replacementPolicy = None
    
    def __init__(self):
        self.memcacheKeyValue = {}
        self.memcacheKeyUploadTime = {}
        self.memcacheKeyUsage = {}
        self.itemNum = 0
        self.itemSize = 0.0
        self.requestNum = 0
        self.hit = 0
        self.miss = 0
        self.missRate = 0.0
        self.hitRate = 0.0

        self.configSize = 1000      # Give 1GB as default.

        
        # specs = sql_connection.get_config_data()
        # try:
        #     self.configSize = specs[0][1]
        #     self.replacementPolicy = specs[0][2]
        #     print(" - Backend.memcahe: Config retrieved from DB.")
        # except IndexError:
        #     self.configSize = 100.0      # Give 100MB initial size as default
        #     self.replacementPolicy = 1
        #     print(" - Backend.memcache: DB doesn't hold any condig, give default values. ")

        print(" - Backend.memcache.__init__ : Init complete, status =>")
        print(" \t configsize: ", self.configSize)
        # print(" \t policy: ", self.replacementPolicy)


    def put(self, key, value, upload_time):
        '''
        This funciton will put a pair into memcache. 
        First, it will inspect if memcache is full (when self.itemSize+putSzie (size of new pair) is greater than self.configSize)
        Otherwise, it will start to remove pairs based on user selected replacement policy. 
        '''

        # invalidate the key, it will be dropped if it exists.
        self.invalidateKey(key)

        print(" - Backend.memcache: f:put, v:configSize:", self.configSize)
        
        putSize = mbytesize_obj(value)
        putSize += mbytesize_obj(key)
        putSize += mbytesize_obj(upload_time)

        self.requestNum += 1

        _exceed_put = (putSize + self.itemSize) > self.configSize
        if _exceed_put:
            print("This node is full. Cannot complete put.")
            return False
        else:
            print("Put success.")
            self.pairAdd(key, value, upload_time)
            return True
        
    
    def get(self, key):
        '''
        This function will search a given key within the memcache. If hit, self.hit and self.requestNum will increase and 
        value & upload_time associate with that key will be returned. If miss, nothing will be returned. 
        '''
        value = None
        upload_time = None
        self.requestNum += 1
        if key in self.memcacheKeyValue:
            value = self.memcacheKeyValue[key]
            upload_time = self.memcacheKeyUploadTime[key]
            self.memcacheKeyUsage[key]+=1

            # Update status with hit/requestNum/hitRate/missRate
            self.hit += 1
            return value, upload_time
        else:
            # Update status with hit/requestNum/hitRate/missRate
            self.miss += 1
            return None, None

    def clear(self):
        '''
        This function will remove all keys and pairs from memcache.
        '''
        self.requestNum += 1
        self.memcacheKeyValue.clear()
        self.memcacheKeyUploadTime.clear()
        self.memcacheKeyUsage.clear()
        self.itemNum = 0
        self.itemSize = 0.0

    def invalidateKey(self, key):
        '''
        To drop a specific key. 
        '''
        self.requestNum += 1
        if key in self.memcacheKeyValue:
            self.pairDelete(key)
        
    def checkSize(self):
        '''
        This function checks whether the size of memcache.
        If the size is greater than configSize, then return true,
        else return false. Also, it returns current total size usage. 
        '''
        size = mbytesize(self.memcacheKeyValue)
        size += mbytesize(self.memcacheKeyUploadTime)
        size += mbytesize(self.memcacheKeyUsage)
        print(" - Backend.memcache.checkSize v:size: ", size)
        return size > self.configSize, size

    def getStatus(self):
        '''
        This function will return multiple items in a list required by `backend.stats.stats_update()`.
        '''
        if self.miss != 0 or self.hit != 0:
            self.missRate = self.miss/(self.hit + self.miss)
            self.hitRate = self.hit/(self.hit + self.miss)
        return [self.itemNum, self.itemSize, self.requestNum, self.missRate, self.hitRate]

    def pairDelete(self, key):
        '''
        This function helps on deleting pairs. With given key, all pairs will be removed from all dict, and status will update. 
        '''
        self.memcacheKeyValue.pop(key)
        self.memcacheKeyUploadTime.pop(key)
        self.memcacheKeyUsage.pop(key) 
        self.itemNum -= 1 
        _exceed, self.itemSize = self.checkSize()

    def pairAdd(self, key, value, upload_time):
        '''
        This function helps on adding pairs. With given key, all pairs will be removed from all dict, and status will update. 
        '''
        self.memcacheKeyValue.update({key:value})
        self.memcacheKeyUploadTime.update({key:upload_time})
        self.memcacheKeyUsage.update({key:0})
        self.itemNum+=1
        _exceed, self.itemSize = self.checkSize()