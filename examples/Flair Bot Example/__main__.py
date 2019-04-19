import praw, psycopg2
import SpazUtils
from SpazUtils import FlairRemoval

from removalreasons import flairList
import config
from BotUtils.CommonUtils import BotServices

# Reddit instance
reddit = praw.Reddit(**config.redditParams)

# Load Config Stuff
sshHost = getattr(config, 'sshHost', None)
publicKey = getattr(config, 'publicKey', None)
sshUsername = getattr(config, 'sshUsername', None)
publicKey = getattr(config, 'publicKey', None)
subredditName = config.subredditName
botName = config.botName

# Psycopg2 instance
params = config.sqlParams

## If database in on another server and ssh tunneling is required
if sshHost and publicKey:
    import paramiko
    from sshtunnel import SSHTunnelForwarder
    pkey = paramiko.pkey.PublicBlob(*publicKey.split(' '))
    server = SSHTunnelForwarder((sshHost, 22), ssh_username=sshUsername, ssh_pkey=pkey, remote_bind_address=('localhost', 5432))
    server.start()
    params['port'] = server.local_bind_port

## Otherwise
postgres = psycopg2.connect(**params)
postgres.autocommit = True
sql: psycopg2.extensions.cursor = postgres.cursor()

subreddit = reddit.subreddit(subredditName)

flairRemoval = FlairRemoval(reddit, subreddit, config.webhook, flairList, botName, sql)
logStream = flairRemoval.logStream
checkModAction = flairRemoval.checkModAction

import logging

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger = logging.getLogger('SpazUtils')
logger.setLevel(logging.INFO)
logger.addHandler(handler)

###starting bot####
print('Starting bot')
def checkLog():
    print('Checking last 25 flair edits...')
    for modAction in subreddit.mod.log(action='editflair', limit=50):
        # try:
            checkModAction(modAction)
        # except Exception as error:
            # print(error)
            # pass

while True:
    # try:
        checkLog()
        # print('Scanning Modlog')
        for modAction in logStream():
            checkModAction(modAction)
    # except Exception as error:
        # print(error)