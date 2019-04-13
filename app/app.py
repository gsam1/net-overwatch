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
                                                                                                                
@app.route('/get_last_hosts_status', methods=['GET'])
def get_last_hosts_status():
    response = dbhandler.get_last_pushed_results()
    timestamp = '{:%Y-%m-%d %H:%M:%S}'.format(response['timestamp'])
    
    # format the response's timestamp
    for item in response['details']:
        item['timestamp'] = '{:%Y-%m-%d %H:%M:%S}'.format(item['timestamp'])
    
    resp = {
        'timestamp': timestamp,
        'summary': {
            'up': response['up'],
            'down': response['down']
        },
        'details': response['details']
    }

    return json.dumps(resp)

@app.route('/get_current_hosts_status', methods=['GET'])
def get_current_hosts_status():
    host_status = HostStatus()
    hosts_stat = host_status.hosts_status()
    total_up = len(hosts_stat['only_up'])
    total_down = len(hosts_stat['only_down'])
    timestamp = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
    details = [host['host'] for host in hosts_stat['overview']]

    resp = {
        'timestamp': timestamp,
        'summary': {
            'up': total_up,
            'down': total_down
        },
        'details': details
    }

    return json.dumps(resp)

# NEW FEATURE
@app.route('/model_training_done', methods=['POST'])
def model_training_done():
    '''A route that tells the bot if the ml model running is done
    '''
    req = request.get_json()
    # tell bot ('Model training done' or custom msg, host training)


if __name__ == '__main__':
    app.run(debug=True)