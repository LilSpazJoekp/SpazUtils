##################################################################################
#------------------------ Flair removal bot by /u/sloth_on_meth. Usernote part by Lil_SpazJoekp--------- #
#todo:
#1. make it easier to add shit
#2. built in killswitch by dming the bot a catchphrase






import time, sys, praw, json, datetime, timeago, requests, modlogstream
#import the blackmagicfuckery that is usernotes
# from UsernoteModule import Usernotes
from discord import embeds
from UsernoteModule import Usernotes
from SpazUtils import FlairRemoval


# #import login info etc
# from DM2_CommonUtils import hours_since
# from DM2_CommonUtils import get_reddit_instance

#import requests + webhook 
# from webhooks import webhook1

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
# reddit = get_reddit_instance("dankbot")
# sub = reddit.subreddit('dankmemes')
time.asctime()
words = ["~~~~~~~~~~~~~~~~~~~"]
webhook1 = "***REMOVED***"

with open('secrets.json') as json_file:  
    data = json.load(json_file)

# Reddit
client_id = data['client_id']
client_secret = data['client_secret']
user_agent = 'python:com.jkpayne.FakeHistoryPornBot:v0.1.3 by /u/Lil_SpazJoekp for /r/fakehistoryporn'
refresh_token = data['refresh_token']
reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent, refresh_token=refresh_token, redirect_uri="http://127.0.0.1/")
sub = reddit.subreddit('Lil_SpazJoekp')
client_idbot = data['client_idold']
refresh_tokenbot = data['refresh_tokenold']
client_secretbot = data['client_secretold']
redditbot = praw.Reddit(client_id=client_idbot, client_secret=client_secretbot, user_agent=user_agent, refresh_token=refresh_tokenbot)
subbot = redditbot.subreddit('Lil_SpazJoekp')

fhpsub = reddit.subreddit('fakehistoryporn')
user = reddit.redditor("Lil_spazjoekp")
submission = reddit.submission(url="https://www.reddit.com/r/Lil_SpazJoekp/comments/9r648f/mod_report_test/")

# sub.submit(flair, url="https://i.redd.it/8bmo4s03q2w11.jpg")


# subredditUsernotes = Usernotes(reddit=reddit, subreddit=submission.subreddit)
# for flair in flair_list:
#     subbot.submit(flair, url="https://i.redd.it/8bmo4s03q2w11.jpg")
# for post in sub.new():
#     for flair in flair_list:
#         if post.title == flair:
#             post.mod.flair(flair)

logStream = modlogstream.stream_generator(sub.mod.log)
action = FlairRemoval(reddit, sub, webhook1).action
while True:
    for modAction in logStream:
        if modAction.action == "editflair" and modAction.target_fullname[:2] == "t3":
                submission = reddit.submission(id=modAction.target_fullname[3:])
                if submission.link_flair_text in flair_list: 
                    actionParam = flair_list[submission.link_flair_text]
                    action(submission, actionParam)
                    print('removed {} post'.format(submission.link_flair_text))

while True:
    try:
        for submission in sub.new(limit=2000):
            
                
            if submission.link_flair_text in flair_list:
                action = flair_list[submission.link_flair_text]
                action(submission, actionParam)
                print('removed {} post'.format(submission.link_flair_text))
                break

            elif submission.link_flair_text in perma_list:
                
                action(submission, actionParam11)
                print('removed {} post'.format(submission.link_flair_text))
                break

            elif submission.link_flair_text in upvote_list:
                content = "The bot has removed a post by " + str(author) + ". It was removed because it was asking for upvotes. the user has been banned for 3 days. here's a link:" + post_link
                
                note = "3 day ban - asking for upvotes"
                ban_reason = 'You were banned for asking for upvotes'
                ban_message = 'You were banned for asking for upvotes.\n\n#[{}]({})'.format(post.title.encode('utf-8'), post_link)
                ban_note = 'You were banned for asking for upvotes'
                reply = reply2
                action(submission, reply, content, note, "ban", True, 3, ban_reason, ban_message, ban_note)
                print('removed {} post'.format(submission.link_flair_text))
                break

            elif submission.link_flair_text in titmc_list:
                submission.mod.remove()
                time.sleep(0.1)
                comment = submission.reply(reply3)
                comment.mod.distinguish(how='yes', sticky=True)
                comment.mod.approve()
                print('removed {} post'.format(submission.link_flair_text))
                break

            elif submission.link_flair_text in personalinfo_list:
                submission.mod.remove()
                time.sleep(0.1)
                requests.post(webhook1, data={"content":"The bot has removed a post by " + str(author) + ". It was removed because it contained personal information. Here's a link:" + post_link})
                
                comment = submission.reply(reply4)
                comment.mod.distinguish(how='yes', sticky=True)
                comment.mod.approve()
                print('removed {} post'.format(submission.link_flair_text))
                subredditUsernotes = Usernotes(reddit=reddit, subreddit=submission.subreddit)
                subredditUsernotes.addUsernote(user=submission.author, note="Personal information", thing=submission, subreddit=submission.subreddit, warningType="spamwatch")
                break

            elif submission.link_flair_text in nadm_list:
                submission.mod.remove()
                time.sleep(0.1)
                requests.post(webhook1, data={"content":"The bot has removed a post by " + str(author) + ". It was removed because it was not a dank meme. Here's a link:" + post_link})
                
                comment = submission.reply(reply5)
                comment.mod.distinguish(how='yes', sticky=True)
                comment.mod.approve()
                print('removed {} post'.format(submission.link_flair_text))
                break

            elif submission.link_flair_text in normie_list:
                submission.mod.remove()
                time.sleep(0.1)
                requests.post(webhook1, data={"content":"The bot has removed a post by " + str(author) + ". It was removed because it was normie trash. Here's a link:" + post_link})
                
                comment = submission.reply(reply6)
                comment.mod.distinguish(how='yes', sticky=True)
                comment.mod.approve()
                print('removed {} post'.format(submission.link_flair_text))
                break

            elif submission.link_flair_text in repost_list:
                submission.mod.remove()
                time.sleep(0.1)
                requests.post(webhook1, data={"content":"The bot has removed a post by " + str(author) + ". It was removed because it was a repost. Here's a link:" + post_link})
                
                comment = submission.reply(reply7)
                comment.mod.distinguish(how='yes', sticky=True)
                comment.mod.approve()
                print('removed {} post'.format(submission.link_flair_text))
                subredditUsernotes = Usernotes(reddit=reddit, subreddit=submission.subreddit)
                subredditUsernotes.addUsernote(user=submission.author, note="repost", thing=submission, subreddit=submission.subreddit, warningType="spamwatch")
                break

            elif submission.link_flair_text in howdy_list:
                submission.mod.remove()
                time.sleep(0.1)
                requests.post(webhook1, data={"content":"The bot has removed a post by " + str(author) + ". It was removed because it was one of those normie howdy posts. Here's a link:" + post_link})
                
                comment = submission.reply(reply8)
                comment.mod.distinguish(how='yes', sticky=True)
                comment.mod.approve()
                print('removed {} post'.format(submission.link_flair_text))
                break

            elif submission.link_flair_text in watermark_list:
                submission.mod.remove()
                time.sleep(0.1)
                requests.post(webhook1, data={"content":"The bot has removed a post by " + str(author) + ". It was removed because it had a watermark. Here's a link:" + post_link})
                
                comment = submission.reply(reply9)
                comment.mod.distinguish(how='yes', sticky=True)
                comment.mod.approve()
                print('removed {} post'.format(submission.link_flair_text))
                subredditUsernotes = Usernotes(reddit=reddit, subreddit=submission.subreddit)
                subredditUsernotes.addUsernote(user=submission.author, note="watch for watermarks", thing=submission, subreddit=submission.subreddit, warningType="spamwatch")
                break

            elif submission.link_flair_text in hatespeech_list:
                submission.mod.remove()
                time.sleep(0.1)
                requests.post(webhook1, data={"content":"The bot has removed a post by " + str(author) + ". It was removed because hatespeech. Here's a link:" + post_link})
                
                comment = submission.reply(reply10)
                comment.mod.distinguish(how='yes', sticky=True)
                comment.mod.approve()
                print('removed {} post'.format(submission.link_flair_text))
                subredditUsernotes = Usernotes(reddit=reddit, subreddit=submission.subreddit)
                subredditUsernotes.addUsernote(user=submission.author, note="Watch out for hatespeech", thing=submission, subreddit=submission.subreddit, warningType="spamwatch")
                break
                
            else:pass   
                
    except:
        print( "Unexpected error:", sys.exc_info()[0])
        raise
