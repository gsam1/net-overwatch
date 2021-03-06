from . import command
import os, sys
import json
import time
from datetime import datetime, timedelta

# try:
#     app_location = os.environ['NMONITOR']
# except:
#     app_location = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# config_location = os.path.join(app_location, 'config')
# sys.path.append(config_location)
# from ..config.config import SlackConfig, ModuleMap




class Event:
    def __init__(self, bot):
        self.bot = bot
        
        self.report_channel = self.bot.slack_config.get_report_channel()#SLACK_CONFIG['report_channel']
        self.report_from = self.bot.slack_config.get_report_from()#SLACK_CONFIG['report_from']
        self.report_to = self.bot.slack_config.get_report_to()#SLACK_CONFIG['report_to']
        self.reporting_interval = self.bot.slack_config.get_reporting_interval()#SLACK_CONFIG['reporting_interval']
        self.command = command.Command(self.bot.dbhandler, self.bot.nmonitor)
        self.starttime = datetime.now()

    def wait_for_event(self):
        # ISSUE: Timeout issue to be fixed
        # Hacky attempt to fix the timeout errors
        # handling the exceptions when they come
        try:
            events = self.bot.slack_client.rtm_read()
        except TimeoutError:
            # put the bot to sleep for 30s
            time.sleep(30)
            # then try again
            events = self.bot.slack_client.rtm_read()
        
        timestamp = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())
        if self.report_time(self.reporting_interval):
            self.handle_event(self.report_to, 'status detailed now', self.report_channel)
        elif (events and len(events) > 0):
            for event in events:
                print(timestamp + str(event))
                self.parse_event(event)

    def report_time(self, interval):
        # interval in minutes
        next_update = self.starttime + timedelta(hours = interval)
        timediff = next_update - datetime.now()
        if (timediff.days*86400 + timediff.seconds) < 5:
            self.starttime = datetime.now()
            return True
        else:    
            return False
                 
    def parse_event(self, event):
        if event and 'text' in event and self.bot.bot_id in event['text']:
            self.handle_event(event['user'], 
                              event['text'].split(self.bot.bot_id)[1].strip().lower(), 
                              event['channel'])
     
    def handle_event(self, user, command, channel):
        if command and channel:
            response = self.command.handle_command(user, command)
            self.bot.slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)