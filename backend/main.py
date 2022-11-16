#from crypt import methods
from os import stat
from flask import render_template, url_for, request,jsonify
from backend import app
from flask import json
import threading
from glob import escape
import time
from ec2_metadata import ec2_metadata


# #Data Model
# from backend.data import Data

# #initialize the database connection
# sql_connection = Data()

# #stats Model
# from backend.stats import Stats
# stats_update = Stats()

# Memcache object
from backend.memcache import Memcache
memcache = Memcache()

# AWS controller
from backend.aws import AWSController
aws_controller = AWSController()

@app.before_first_request
def run_when_start():
    task = threading.Thread(target = cloud_watch_update)
    task.start()

def cloud_watch_update():
    while True:
        missRate = memcache.getStatus()[3]
        instanceID = ec2_metadata.instance_id
        response = aws_controller.update_cloud_watch(missRate, instanceID)
        print(response)
        time.sleep(60)

@app.route('/')
def main():
    return "Here is backend"

#This is front back call example
@app.route('/test',methods=['GET'])
def test():
    message = "Hello from node."
    #generate the json response
    response = jsonify({
        "success":"true",
        "message":message
    })
    #return json response
    return response, 200

# @app.route('/statistics')
# def stats():
#     '''
#     When first request initilized from browser, frondend will call this api to active a thread to 
#     record status. 
#     '''
#     print(" * Backend is running.")
#     thread = threading.Thread(target = stats_update.stats_update_t2, args = (memcache, ))
#     thread.start()
#     print(" * Starts threading.")
#     return jsonify({"Messsge":"True, threading starts"}), 200
    
    
@app.route('/get', methods=['GET', 'POST'])
def get():
    '''
    Seach a key in memcache. 
    '''
    # Get key through different approaches.
    key = None
    if request.method == 'GET' and 'key' in request.args:
        key  = escape(request.args.get("key"))
    elif request.method == 'POST':
        key = request.form.get('key')

    value, upload_time = memcache.get(key)
    
    if value != None and upload_time != None:
        print(" - Backend.main.get : Key found in backend! ")
        response = {"key":key, "value":value, "upload_time":upload_time}

        # NOTICE: create a dict and return it with `jsonify`. Another argument after it is the status code. 
        return jsonify(response), 200

    else:
        response = {"Message":"Miss"}
        return jsonify(response), 400



@app.route('/put', methods=['POST'])
def put():
    '''
    Put a key, value (encoded image), and upload_time into memcache. 
    '''
    key = request.form.get('key')
    value = request.form.get('value')
    upload_time = request.form.get('upload_time')

    print(" - Backend: key, upload_time: ", key, upload_time)
    
    result = memcache.put(key, value, upload_time)
    print(" - Backend.main.put v:result: ", result)

    if result:
        returnCode = 200
        returnMessage = {"Message":"Put success"}
    else:
        returnCode = 400
        returnMessage = {"Message":"Put failed"}

    return jsonify(returnMessage), returnCode

@app.route('/clear', methods=['GET'])
def clear():
    '''
    Clean memcache. 
    '''
    memcache.clear()
    return jsonify({"Message":"Clear down"}), 200

@app.route('/config', methods=['GET'])
def config():
    '''
    Set memcache configration.
    '''
    size = 100.0
    replacementPolicy = 1
    if "size" in request.args and "replacement_policy" in request.args:
        size = escape(request.args.get("size"))
        replacementPolicy = escape(request.args.get("replacement_policy"))
        memcache.refreshConfiguration(size, replacementPolicy)

    return jsonify({"Message":"Success update config"}), 200

@app.route('/handshake', metods=["GET"])
def handshake():
    '''
    This function is used for hand shake with front end
    '''
    return jsonify({
        "success":"true",
        "status":200
    })

