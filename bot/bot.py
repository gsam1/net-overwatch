import os
import time
import re
import json
from slackclient import SlackClient

TOKEN = json.load(open('./config/slack.json', 'r'))['token']

# instantiate Slack client

slack_client = SlackClient(TOKEN)

if slack_client.rtm_connect(with_team_state=False):
    print("Successfully connected, listening for events")
    while True:
        print(slack_client.rtm_read())
         
        time.sleep(1)
else:
    print("Connection Failed")

# print(events)