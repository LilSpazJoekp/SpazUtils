##################################################################################
#------------------------ Flair removal bot by /u/sloth_on_meth. Usernote part by Lil_SpazJoekp--------- #
#todo:
#1. make it easier to add shit
#2. built in killswitch by dming the bot a catchphrase

import time, sys, praw, json, datetime, timeago, requests, modlogstream

from SpazUtils import FlairRemoval

# #import login info etc
from DM2_CommonUtils import hours_since#?
from DM2_CommonUtils import get_reddit_instance

#import requests + webhook 
from webhooks import webhook1

#import the removal reasons
from removalreasons import *

flair_list = {
    "911": actionParam,
    "9/11": actionParam,
    "vt7": actionParam,
    "school shooting meme": actionParam11,
    "vt14": actionParam11,
    "afu": actionParam2,
    "titmc": actionParam3,
    "nadm": actionParam4,
    "nt": actionParam5,
    "pi": actionParam6,
    "rpost": actionParam7,
    "hp": actionParam8,
    "1337bububu": actionParam8,
    "wm": actionParam9,
    "hs": actionParam10
      }
reddit = get_reddit_instance("dankbot")
sub = reddit.subreddit('dankmemes')

logStream = modlogstream.stream_generator(sub.mod.log)
action = FlairRemoval(reddit, sub, webhook1).action

logStream = modlogstream.stream_generator(sub.mod.log)
action = FlairRemoval(reddit, sub, webhook1).action
print('Starting bot')
def checkLog():
    print('Checking last 25 flair edits...')
    for modAction in sub.mod.log(action='editflair', limit=250):
        try:
            if modAction.target_fullname:
                if modAction.target_fullname[:2] == "t3" and modAction.details == "flair_edit":
                    submission = reddit.submission(id=modAction.target_fullname[3:])
                    print(submission)
                    removed = []
                    if not os.path.isfile('removed'):
                        f = open('removed', 'w')
                        f.close
                    with open('removed', 'r') as f:
                        removed = f.read().split('\n')
                    if submission.link_flair_text in flair_list:
                        if not submission.shortlink in removed:
                            print('Found {}'.format(submission.link_flair_text))
                            actionParam = flair_list[submission.link_flair_text]
                            action(submission, actionParam)
                            print('removed {} post'.format(submission.link_flair_text))
                            with open('removed', 'a') as f:
                                f.write('{}\n'.format(submission.shortlink))
                        else:
                            print('Already removed: {}'.format(submission.id))
        except Exception as error:
            print(error)

while True:
    try:
        checkLog()
        print('Scanning Modlog')
        for modAction in logStream:
            if modAction.target_fullname:
                if modAction.action == "editflair" and modAction.target_fullname[:2] == "t3":
                    submission = reddit.submission(id=modAction.target_fullname[3:])
                    removed = []
                    with open('removed', 'r') as f:
                        removed = f.read().split('\n')
                    if submission.link_flair_text in flair_list:
                        if not submission.shortlink in removed:
                            print('Found {}'.format(submission.link_flair_text))
                            actionParam = flair_list[submission.link_flair_text]
                            action(submission, actionParam)
                            print('removed {} post'.format(submission.link_flair_text))
                            with open('removed', 'a') as f:
                                f.write('{}\n'.format(submission.shortlink))
                        else:
                            print('Already removed: {}'.format(submission.id))
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise
