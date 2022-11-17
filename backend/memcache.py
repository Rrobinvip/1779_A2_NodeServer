import random
from backend.helper import mbytesize, mbytesize_obj, api_call
# from backend.data import Data
# sql_connection = Data()
from backend.aws import AWSController
from ec2_metadata import ec2_metadata
aws_controller = AWSController()

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
    replacementPolicy = None
    
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
        
        # Call manager to get status. Always assuming master is running.
        master_ip = aws_controller.get_master_instance_ip_address()

        if master_ip == None:
            url = "localhost:5000/manager/"
        else:
            url = master_ip+":5000/manager/"
        specs = api_call(url, "GET", "api/get_config")

        if specs.status_code == 200:
            config = specs.json()
            self.configSize = config['size']
            self.replacementPolicy = config['replace_policy']
            print(" - Backend.memcache.__init__ : Init from manager. =>")
        else:
            self.configSize = 100.0      # Give 100MB initial size as default
            self.replacementPolicy = 1
            print(" - Backend.memcache.__init__ : Init from default. =>")


        print(" - Backend.memcache.__init__ : Init complete, status =>")
        print(" \t configsize: ", self.configSize)
        print(" \t policy: ", self.replacementPolicy)

        pass

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
        
        if self.spaceSwap(putSize):
            self.pairAdd(key, value, upload_time)
            print(" - Backend.memcache.put : a new key stored.")
            return True
        else:
            print(" - Backend.memcache.put : memcache cannot hold this pair.")
            return False

    def spaceSwap(self, putSize):
        '''
        This function tests if a new pair can be put into the memcache. 

        - If there are many pairs already in the memcache, this function will start to delete pairs based on users config. Stop when no pairs or enough space.
        - If there has no pairs in memcache, put putSize is still larger than the config size, it will return false and lead to a failure on put. 
        '''
        _exceed_put = (putSize + self.itemSize) > self.configSize
        while _exceed_put and self.itemNum != 0:
            if self.replacementPolicy == 1:
                self.removeLeastRecentUse()
            else:
                self.randomRemove()
            _exceed_put = (putSize + self.itemSize) > self.configSize
        if _exceed_put and self.itemNum == 0:
            print(" - Backend.memcache.spaceSwap : No items, but new file is too large. Increase memcache config size. This file will not be stored in memcache")
            return False
        else:
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
        
    def refreshConfiguration(self, size, replacement_policy):
        '''
        This function will reset memcache config. After reset config, if current item size is larger than config size, memcache
        will keep removing items based on replacement policy until some conditions are meet. 
        '''
        self.requestNum += 1

        print(" - Backend.memcache: refreshing policy with p:{} s:{}".format(replacement_policy, float(size)))

        self.configSize = float(size)
        self.replacementPolicy = replacement_policy

        _exceed, size = self.checkSize()
        print(" - Backend.memcache.put v:_exceed: ", _exceed)
        if _exceed == False:
            return True
        else:
            if self.itemNum != 0:
                notEmpty = True
            else:
                notEmpty = False
                
            while _exceed and notEmpty:
                if self.replacementPolicy == 1:
                    result =  self.removeLeastRecentUse()
                    if result == None:
                        notEmpty = False
                else:
                    result = self.randomRemove()
                    if result == None:
                        notEmpty = False                        
                _exceed, size = self.checkSize()
            if not notEmpty and _exceed:
                print("Very rare situation happened. It's empty but size is already too large to put any pairs.")
                print("Consider add more default size. ")
                return False
            return True
        
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

    def randomRemove(self):
        '''
        This function helps reandom remove an item from memcache.
        it will return the removed key, if the value is none, then the remove
        action fails
        '''
        key = None
        if self.itemNum != 0:
            key = random.choice(list(self.memcacheKeyValue.keys()))
            self.pairDelete(key)
        return key


    def removeLeastRecentUse(self):
        '''
        This function helps remove the least recent use key.
        It will return the removed key, if key is none, then the remove
        action fails.
        '''
        key = None
        if self.itemNum != 0:
            key = min(self.memcacheKeyUsage)
            self.pairDelete(key)
        return key
    

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
