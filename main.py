import os, sys
from bot.bot import Bot
from config.config import SlackConfig, Options, DBOptions
from db.dbhandler import DBHandler, Hosts, Checks 
from netmonitor.monitor import HostStatus

from multiprocessing import Process

class DotDict(dict):
    def __getattr__(self, key):
        return self[key]
    def __setattr__(self, key, val):
        if key in self.__dict__:
            self.__dict__[key] = val
        else:
            self[key] = val


def start_bot():
    '''
        Start the slack chatbot
    '''
    slackconfig = SlackConfig()
    dboptions = DBOptions()
    dbhandler = DBHandler(remotedb_uri=dboptions.get_db_uri())
    # there is probably a better way of doing this but..
    dbhandle = DotDict({
        'DBHandler': DBHandler,
        'Options': Options,
        'Hosts': Hosts,
        'Checks': Checks
    })

    netmonitor = HostStatus(dbhandle)

    bot = Bot(slackconfig, dbhandler, netmonitor)

def start_api():
    '''
        Start the reporting api
    '''
    os.system('bash start_api.sh')

def main():
    '''
        Runs Everything
    '''
    bot = Process(target = start_bot)
    api = Process(target = start_api)

    bot.start()
    api.start()



if __name__ == '__main__':
    main()