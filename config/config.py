import os
import json


class Config:
    def __init__(self):
        self.config_json = json.load(open(os.path.dirname(os.path.realpath(__file__)) + '/json/configuration.json'))

class SlackConfig(Config):
    def __init__(self):
        super().__init__()
        self.slack_config = self.config_json['slack_api']
    
    def get_token(self):
        return self.config_json['token']
    
    def get_report_channel(self):
        return self.config_json['report_channel']
    
    def get_report_from(self):
        return self.config_json['report_from']
    
    def get_report_to(self):
        return self.config_json['report_to']
    
    def get_reporting_interval(self):
        return self.config_json['reporting_interval']


class Options(Config):
    def __init__(self):
        super().__init__()
        self.options_config = self.config_json['options']
    
    def get_response_time(self):
        return self.options_config['response-time']

class ModuleMap(Config):
    def __init__(self):
        super().__init__()
        self.module_map = self.config_json['module_map']
    
    def get_bot_loc(self):
        return self.module_map['bot']
    
    def get_cli_loc(self):
        return self.module_map['cli']
    
    def get_netmonitor_loc(self):
        return self.module_map['netmonitor']
    
    def get_db_loc(self):
        return self.module_map['db']