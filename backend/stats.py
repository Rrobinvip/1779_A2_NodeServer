# from os import stat
# from backend.data import Data
# import time
# from backend.memcache import Memcache

# class Stats:
    
#     mysql_connection = Data()

#     def __init__(self):
#         pass

#     def stats_update(self,itemNum,itemSize,requestNum,missRate,hitRate):
#         '''
#         This function update the statistics every 5 second.

#         ## Warning, this function is not working properly. 
#         '''
#         while True:
#             self.mysql_connection.insert_stat_data(itemNum,itemSize,requestNum,missRate,hitRate)
#             time.sleep(5)


#     def stats_update_t2(self, memcache:Memcache):
#         '''
#         Fixed stats_update, data in original function is completely static. 
#         '''
#         while True:
#             status = memcache.getStatus()
#             self.mysql_connection.insert_stat_data(status[0], status[1], status[2], status[3], status[4])
#             time.sleep(5)

