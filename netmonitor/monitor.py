from multiping import MultiPing
import json


HOSTS = json.load(open('./config/hosts.json'))['hosts']
HOSTS_TO_PING = [HOSTS[key] for key in HOSTS.keys()]

mp = MultiPing(HOSTS_TO_PING)

mp.send()

responses, no_responses = mp.receive(2)

print(responses)
print(no_responses)