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

while True:
    try:
        for modAction in logStream:
            if modAction.action == "editflair" and modAction.target_fullname[:2] == "t3":
                submission = reddit.submission(id=modAction.target_fullname[3:])
                if submission.link_flair_text in flair_list: 
                    actionParam = flair_list[submission.link_flair_text]
                    action(submission, actionParam)
                    print('removed {} post'.format(submission.link_flair_text))
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise