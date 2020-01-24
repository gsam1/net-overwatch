#!/usr/bin/python3
from flask import Flask, request
from flask import jsonify
import sys, os, json
import datetime
# DEM DIRTY HACKS
par_dir = os.path.dirname(os.getcwd())
config_location = os.path.join(par_dir, 'config')
netmonitor_location = os.path.join(par_dir, 'netmonitor')
db_location = os.path.join(par_dir, 'db')
bot_location = os.path.join(par_dir, 'bot')
sys.path.append(config_location)
sys.path.append(bot_location)
sys.path.append(netmonitor_location)
sys.path.append(db_location)

from config import SlackConfig
from dbhandler import DBHandler
from monitor import HostStatus
from slackclient import SlackClient


ENV = 'development'
app = Flask(__name__)
dbhandler = DBHandler()

####### Optional Slack Client
TOKEN = SlackConfig().get_token()
sc = SlackClient(TOKEN)


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
@app.route('/task_done', methods=['POST'])
def task_done():
    '''
        A route that accepts a json with a report that a task is done
        Example structure of the request json
        {
            "host": host which reports that the task is done,
            "task_desc": short description of the task performed
        }
    '''
    req = request.get_json()
    req = json.load(req)
    host = req['host']
    task = req['task_desc']
    msg = '<@' + SlackConfig().get_report_to() + '>: HOST: ' + host + ' | ' + task

    # tell bot ('Model training done' or custom msg, host training)
    sc.api_call("chat.postMessage", 
                channel=SlackConfig().get_report_channel(), 
                text=msg, 
                user=SlackConfig().get_report_from())

    return 'Message Sent'

# SHORT API for the specific purpose of reporting model_training
@app.route('/task/ml_td', methods=['GET'])
def model_training_done():
    '''
        A route that tells the bot if the ml model running is done.

    '''
    host = request.args.get('host')
    msg = '<@' + SlackConfig().get_report_to() + '>: HOST: ' + host + ' | Model Training Done' 
    sc.api_call("chat.postMessage", 
                channel=SlackConfig().get_report_channel(), 
                text=msg, 
                user=SlackConfig().get_report_from())

    
    return 'Message Sent'


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)