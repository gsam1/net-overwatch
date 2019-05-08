import os, sys
import time
import re
import json
import event
import command
from slackclient import SlackClient

try:
    app_location = os.environ['NMONITOR']
except:
    app_location = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

config_location = os.path.join(app_location, 'config')
sys.path.append(config_location)
from config import SlackConfig, ModuleMap

TOKEN = SlackConfig().get_token()

class Bot(object):
    def __init__(self):
        self.slack_client = SlackClient(TOKEN)
        self.bot_name = 'overwatch'
        self.bot_id = self.get_bot_id()
         
        if self.bot_id is None:
            exit('Error, could not find ' + self.bot_name)
     
        self.event = event.Event(self)
        self.listen()
     
    def get_bot_id(self):
        api_call = self.slack_client.api_call('users.list')
        if api_call.get('ok'):
            # retrieve all users so we can find our bot
            users = api_call.get('members')
            for user in users:
                if 'name' in user and user.get('name') == self.bot_name:
                    return '<@' + user.get('id') + '>'
             
            return None
             
    def listen(self):
        if self.slack_client.rtm_connect(with_team_state=False):
            print('Successfully connected, listening for commands')
            while True:
                # random disconnet fix, because of the Web Socket Closed
                try:
                    self.event.wait_for_event()
                except:
                    self.listen()
                time.sleep(1)
        else:
            exit('Error, Connection Failed')


if __name__ == '__main__':
    Bot()