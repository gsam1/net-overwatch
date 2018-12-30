import command
import json
from datetime import datetime, timedelta

REPORT_CHANNEL = json.load(open('./config/slack.json', 'r'))['report_channel']
REPORT_FROM = json.load(open('./config/slack.json', 'r'))['report_from']
REPORT_TO = json.load(open('./config/slack.json', 'r'))['report_to']
REPORTING_INTERVAL = json.load(open('./config/slack.json', 'r'))['reporting_interval']


class Event:
    def __init__(self, bot):
        self.bot = bot
        self.command = command.Command()
        self.starttime = datetime.now()

    def wait_for_event(self):
        events = self.bot.slack_client.rtm_read()
        

        if self.report_time(2):
            self.handle_event(REPORT_TO, 'status detailed now', REPORT_CHANNEL)
        elif (events and len(events) > 0):
            for event in events:
                print(event)
                self.parse_event(event)

    def report_time(self, interval):
        # interval in minutes
        next_update = self.starttime + timedelta(minutes = interval)
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