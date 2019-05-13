from flask import Flask, request
from flask import jsonify
import sys, os, json
import datetime
# DEM DIRTY HACKS
try:
    app_location = os.environ['NMONITOR']
except:
    app_location = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

config_location = os.path.join(app_location, 'config')
sys.path.append(config_location)
from config import SlackConfig, ModuleMap
db_location = ModuleMap().get_db_loc()
netmonitor_location = ModuleMap().get_netmonitor_loc()
bot_location = ModuleMap().get_bot_loc()
sys.path.append(bot_location)
sys.path.append(netmonitor_location)
sys.path.append(db_location)
from dbhandler import DBHandler
from monitor import HostStatus
from slackclient import SlackClient



ENV = 'development'
app = Flask(__name__)
dbhandler = DBHandler()

####### Optional Slack Client
CONFIG = json.load(open(os.path.dirname(os.path.realpath(bot_location)) + '/bot/config/slack.json', 'r'))
sc = SlackClient(CONFIG['token'])
###### ROUTES

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
    host = req['host']
    msg = ''
    if 'msg' in req.keys():
        msg = req['msg']
    else:
        msg = 'Training of model complete!'
    # add mention
    msg = '<@' + CONFIG['report_to'] + '>: HOST: ' + host + ' | ' + msg
        
    # tell bot ('Model training done' or custom msg, host training)
    sc.api_call("chat.postMessage", channel=CONFIG['report_channel'], text=msg, user=CONFIG['report_from'])

    return 'Message Sent'


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)