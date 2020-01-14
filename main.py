from bot.bot import Bot
from config.config import SlackConfig, Options
from db.dbhandler import DBHandler, Hosts, Checks 
from netmonitor.monitor import HostStatus

class DotDict(dict):
    def __getattr__(self, key):
        return self[key]
    def __setattr__(self, key, val):
        if key in self.__dict__:
            self.__dict__[key] = val
        else:
            self[key] = val


def main():
    '''
        Runs Everything
    '''
    slackconfig = SlackConfig()
    dbhandler = DBHandler()
    # there is probably a better way of doing this but..
    dbhandle = DotDict({
        'DBHandler': DBHandler,
        'Options': Options,
        'Hosts': Hosts,
        'Checks': Checks
    })

    netmonitor = HostStatus(dbhandle)

    bot = Bot(slackconfig, dbhandler, netmonitor)


    



if __name__ == '__main__':
    main()