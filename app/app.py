from flask import Flask, request
from flask import jsonify
import sys, os, json
import datetime
# DEM DIRTY HACKS
try:
    app_location = os.environ['NMONITOR']
except:
    app_location = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

db_location = json.load(open(os.path.join(app_location, 'configurator/module_map.json')))['db']
netmonitor_location = json.load(open(os.path.join(app_location, 'configurator/module_map.json')))['netmonitor']
sys.path.append(netmonitor_location)
sys.path.append(db_location)
from dbhandler import DBHandler
from monitor import HostStatus


ENV = 'development'
app = Flask(__name__)
dbhandler = DBHandler()

@app.route('/')
def index():
    return 'Network Overwatch API'

@app.route('/add_host', methods=['POST'])
def add_host():
    req = request.get_json()
    dbhandler.push_host(req)

    return 'Host Pushed'

@app.route('/update_host', methods=['POST'])
def update_host():
    req = request.get_json()
    hostname = req['host']
    # get the host which to update
    host_id = dbhandler.get_host_id(hostname)
    # update the hostname
    dbhandler.update_host(id=host_id, params_to_update=req['vars'])

    return f'Host {hostname} updated'
    



if __name__ == '__main__':
    app.run(debug=True)