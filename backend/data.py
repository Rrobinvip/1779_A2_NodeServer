from backend.config import Config
import mysql.connector as MySQL
from datetime import datetime
from mysql.connector import errorcode

#This class provide backend database access. It provides funciton to query data from
#and insert into configuration and statistics database
#Already tested

# class Data:
#     cursor = None
#     cnx = None

#     def __init__(self):
#         try:
#             #connect to database
#             self.cnx = MySQL.connect(
#                 user = Config.DB_CONFIG["user"],
#                 password = Config.DB_CONFIG["password"],
#                 host = Config.DB_CONFIG["host"],
#                 database = Config.DB_CONFIG["database"]
#             )
#         except MySQL.Error as err:
#             #add database error code
#             if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
#                 print("Something wrong with user name and password")
#             elif err.errno == errorcode.ER_BAD_DB_ERROR:
#                 print("Database does not exist")
#             else:
#                 print(err)
        
#         #initialize cursor of database
#         self.cursor = self.cnx.cursor()

#         print(" - Backend DB Connection Success.")

#     #get the data from the configuration table
#     #this function will return the latest memcache config
#     def get_config_data(self):
#         #select the latest configuraiton from the database
#         query = """
#                 SELECT * FROM configuration WHERE id = (
#                     SELECT MAX(id) From configuration
#                 )
#                 """
#         self.cnx.commit()
#         self.cursor.execute(query)
#         print(" - Backend.data.get_config_data: Config Query Executed.")
#         data = self.cursor.fetchall()
#         return data
    
#     #insert into the configuration database
#     #capacity: the capacity of the memcache
#     #policy: 0 for Random Replacement, 1 for Least Recently Used
#     def insert_config_data(self,capacity,policy):

#         query = """
#                 INSERT INTO `configuration` (`capacity`,`replacePolicy`)
#                 VALUES("{}","{}");
#         """.format(capacity,policy)

#         self.cursor.execute(query)
#         self.cnx.commit()

#     #get the data from the statistics table
#     #this function will return the latest statistics in the table
#     def get_stat_data(self):
#         #select the latest configuration from the database
#         query = """
#                 select * from statistics
#                 ORDER BY `id` DESC
#                 LIMIT 120;
#                 """
#         self.cnx.commit()
#         self.cursor.execute(query)
#         print("Statistics Query Executed")
#         data = self.cursor.fetchall()
#         # print("Statistics data at backend: ", data)
#         return data
    
#     #insert data into statistics table
#     #itemNum: the number of item
#     #itemSize: the size of the current item in memcache
#     #requestNum: the number of request
#     #missRate: miss times/ number of request
#     #hitRate: hit times/ number of request
#     def insert_stat_data(self,itemNum,itemSize,requestNum,missRate,hitRate):
#         now = datetime.now()
#         fixed_now = now.strftime('%Y-%m-%d %H:%M:%S')
#         query = """
#                 INSERT INTO `statistics` (`itemNum`,`itemSize`,`requestNum`,`missRate`,`hitRate`,`datetime`)
#                 VALUES("{}","{}","{}","{}","{}","{}");
#         """.format(itemNum,itemSize,requestNum,missRate,hitRate,fixed_now)
#         self.cursor.execute(query)
#         self.cnx.commit()
    
    
    
        












    
        
    


        