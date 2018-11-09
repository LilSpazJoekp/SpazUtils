import time
import sys
import praw

#import the blackmagicfuckery that is usernotes
from UsernoteModule import Usernotes



#import login info etc
from DM2_CommonUtils import hours_since
from DM2_CommonUtils import get_reddit_instance

#import requests + webhook 
import requests
from webhooks import webhook1

#import the removal reasons
from removalreasons import *

flair_list = ["911", "9/11", "vt7"]
perma_list = ["school shooting meme", "vt14"]
upvote_list = ["afu"]
titmc_list = ["titmc"]
nadm_list = ["nadm"]
normie_list = ["nt"]
personalinfo_list = ["pi"]
repost_list = ["rpost"]
howdy_list = ["hp"]
usernote_list = ["1337bububu"]
watermark_list = ["wm"]
hatespeech_list = ["hs"]

reddit = get_reddit_instance("dankbot")
sub = reddit.subreddit('dankmemes')

words = ["~~~~~~~~~~~~~~~~~~~"]



while True:
    try:
        for submission in sub.new(limit=2000):
            title = submission.title.lower()
            for word in words:
                post = submission
                post_link = 'https://reddit.com' + post.permalink
                author = submission.author
                
                if submission.link_flair_text in flair_list:
                    submission.mod.remove()
                    time.sleep(0.1)
                    requests.post(webhook1, data={"content":"The bot has removed a post by " + str(author) + ". It was removed because it was violating the tragedies rules. the user has been banned for 7 days. here's a link:" + post_link})
                    sub.banned.add(submission.author, duration=7, ban_reason='You were banned for posting a meme about a violent tragedy', ban_message='You were banned for posting a meme about a violent tragedy.\n\n#[{}]({})'.format(post.title.encode('utf-8'), post_link), note='You were banned for posting a meme about a violent tragedy')
                    comment = submission.reply(reply)
                    comment.mod.distinguish(how='yes', sticky=True)
                    comment.mod.approve()
                    subredditUsernotes = Usernotes(reddit=reddit, subreddit=submission.subreddit)
                    subredditUsernotes.addUsernote(user=submission.author, note="7 day ban  - tragedy meme", thing=submission, subreddit=submission.subreddit, warningType="ban")
                    print('removed {} post'.format(submission.link_flair_text))
                    break
                elif submission.link_flair_text in perma_list:
                    submission.mod.remove()
                    time.sleep(0.1)
                    requests.post(webhook1, data={"content":"The bot has removed a post by " + str(author) + ". It was removed because it was violating the tragedies rules. the user has been banned for 14 days. here's a link:" + post_link})
                    sub.banned.add(submission.author, duration=14, ban_reason='You were banned for posting a meme about a violent tragedy', ban_message='You were banned for posting a meme about a violent tragedy.\n\n#[{}]({})'.format(post.title.encode('utf-8'), post_link), note='You were banned for posting a meme about a violent tragedy')
                    comment = submission.reply(reply)
                    comment.mod.distinguish(how='yes', sticky=True)
                    comment.mod.approve()
                    subredditUsernotes = Usernotes(reddit=reddit, subreddit=submission.subreddit)
                    subredditUsernotes.addUsernote(user=submission.author, note="14 day ban  - tragedy meme", thing=submission, subreddit=submission.subreddit, warningType="ban")
                    print('removed {} post'.format(submission.link_flair_text))
                    break
                elif submission.link_flair_text in upvote_list:
                    submission.mod.remove()
                    time.sleep(0.1)
                    requests.post(webhook1, data={"content":"The bot has removed a post by " + str(author) + ". It was removed because it was asking for upvotes. the user has been banned for three days. here's a link:" + post_link})
                    sub.banned.add(submission.author, duration=3, ban_reason='You were banned for asking for votes, reposts or comments', ban_message='You were banned for asking for votes, reposts or comments.\n\n#[{}]({})'.format(post.title.encode('utf-8'), post_link), note='You were banned for asking for votes, reposts or comments.')
                    comment = submission.reply(reply2)
                    comment.mod.distinguish(how='yes', sticky=True)
                    comment.mod.approve()
                    subredditUsernotes = Usernotes(reddit=reddit, subreddit=submission.subreddit)
                    subredditUsernotes.addUsernote(user=submission.author, note="3 day ban  - asking for upvotes", thing=submission, subreddit=submission.subreddit, warningType="ban")
                    print("removed {} post".format(submission.link_flair_text))
                    break
                elif submission.link_flair_text in titmc_list:
                    submission.mod.remove()
                    time.sleep(0.1)
                    requests.post(webhook1, data={"content":"The bot has removed a post by " + str(author) + ". It was removed because the title was the meme caption. Here's a link:" + post_link})
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
                    requests.post(webhook1, data={"content":"The bot has removed a post by " + str(author) + ". It was removed because it was one of those normie howdy posts. Here's a link: " + post_link})
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
                    #so excited for this lol
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
                #elif submission.link_flair_text in usernote_list:
                #    time.sleep(0.1)
                #    requests.post(webhook1, data={"content":"usernote added!" + post_link})
                #    print('usernoted {} shieeet'.format(submission.link_flair_text))
                #    subredditUsernotes = Usernotes(reddit=reddit, subreddit=submission.subreddit)
                #    subredditUsernotes.addUsernote(user=submission.author, note="gay mod test note", thing=submission, subreddit=submission.subreddit, warningType="ban")
                #    break
                
                else:pass   
                
    except:
        print( "Unexpected error:", sys.exc_info()[0])
        raise
