import time, praw, json, datetime, timeago, requests, base64, zlib
from typing import Union
from discord import embeds

class FlairRemoval:
    
    def __init__(self, reddit: praw.Reddit, subreddit: praw.reddit.models.Subreddit, webhook: str):
        self.reddit = reddit
        self.sub = subreddit
        self.webhook = webhook

    def action(self, submission: praw.models.reddit.submission.Submission, action: dict):
        submission.mod.remove()
        time.sleep(0.1)
        try:
            if 'ban' in action:
                self.setBan(submission, action['ban'])
        except Exception as error:
            print(error)
        comment = submission.reply(action['commentReply'])
        comment.mod.distinguish(how='yes', sticky=True)
        comment.mod.approve()
        data = {"embeds": self.generateEmbed(submission, action)}
        requests.post(self.webhook, json=data)
        if 'usernote' in action:
            usernote = action['usernote']
            subredditUsernotes = Usernotes(reddit=self.reddit, subreddit=submission.subreddit)
            subredditUsernotes.addUsernote(user=submission.author, note=usernote['usernote'], thing=submission, subreddit=submission.subreddit, warningType=usernote['usernoteWarningType'])
            
    def generateEmbed(self, submission: praw.models.reddit.submission.Submission, params: dict):
        embed = embeds.Embed(title="Bot Removal Notification", url=submission.shortlink, description=params['description'])
        if not submission.is_self:
            embed.set_image(url=submission.url)
        embed.add_field(name="Submission:", value="[{0.title}]({0.shortlink})".format(submission), inline=False)
        embed.add_field(name="Author:", value="[{0.author.name}](https://reddit.com/user/{0.author.name})".format(submission), inline=True)
        embed.add_field(name="Posted At:", value=time.strftime('%b %d, %Y %I:%M %p %Z', time.gmtime(submission.created_utc)), inline=True)
        embed.add_field(name="Score:", value="{:,}".format(submission.score), inline=True)
        embed.add_field(name="Comments:", value="{:,}".format(submission.num_comments), inline=True)
        for modAction in submission.subreddit.mod.log(action="editflair"):
            if modAction.target_fullname == submission.fullname:
                embed.add_field(name="Removed By:", value="{}".format(modAction._mod), inline=True)
        if 'ban' in params:
            ban = params['ban']
            embed.add_field(name="Ban Duration:", value="{} days".format(ban['duration']), inline=True)
        modReports = self.parseModReports(submission)
        if modReports:
            if not modReports[0][1] == 0:
                embed.add_field(name="Mod Reports ({}):".format(modReports[0][1]), value=modReports[0][0], inline=True)
            if not modReports[1][1] == 0:
                embed.add_field(name="Mod Reports Dismissed ({}):".format(modReports[1][1]), value=modReports[1][0], inline=True)
        userReports = self.parseReports(submission)
        if userReports:    
            if not userReports[0][1] == 0:
                embed.add_field(name="User Reports ({}):".format(userReports[0][1]), value=userReports[0][0], inline=True)
            userReports = self.parseReports(submission)
            if not userReports[1][1] == 0:
                embed.add_field(name="User Reports Dismissed ({}):".format(userReports[1][1]), value=userReports[1][0], inline=True)
        usernotesString = self.parseUsernotes(Usernotes(reddit=self.reddit, subreddit=submission.subreddit), submission.author.name)
        if usernotesString:
            embed.add_field(name="Usernotes:", value=usernotesString, inline=False)
        embed.set_footer(text=time.strftime('%B %d, %Y at %I:%M:%S %p %Z', time.gmtime()))
        return [embed.to_dict()]
    
    def setBan(self, submission: praw.models.reddit.submission.Submission, params: dict):
        if "duration" in params and params["duration"] > 0:
            self.sub.banned.add(submission.author, duration=params["duration"], ban_reason=params["ban_reason"], ban_message=params["ban_message"], note=params["ban_note"])
        else:
            self.sub.banned.add(submission.author, duration=params["duration"], ban_reason=params["ban_reason"], ban_message=params["ban_message"].format(submission), note=params["ban_note"])

    def parseReports(self, submission: praw.models.reddit.submission.Submission):
        userReports = []
        userReports = []
        userReports = submission.user_reports
        if "user_reports_dismissed" in vars(submission):
            userReports.append(submission.user_reports_dismissed[0])
        reportString = "{0[1]}: {0[0]}\n"
        final = ""
        for report in userReports:
            final += reportString.format(report)
        dismissedFinal = ""
        for report in userReports:
            dismissedFinal += reportString.format(report)
        if len(final) == 0 and len(dismissedFinal) == 0:
            return
        else:
            return ((final, len(userReports)), (dismissedFinal, len(userReports)))

    def parseModReports(self, submission: praw.models.reddit.submission.Submission):
        modReports = []
        modReportsDismissed = []
        modReports = submission.mod_reports
        if "mod_reports_dismissed" in vars(submission):
            modReportsDismissed.append(submission.mod_reports_dismissed[0])
        reportString = "{0[1]}: {0[0]}\n"
        final = ""
        for report in modReports:
            final += reportString.format(report)
        dismissedFinal = ""
        for report in modReportsDismissed:
            dismissedFinal += reportString.format(report)
        if len(final) == 0 and len(dismissedFinal) == 0:
            return
        else:
            return ((final, len(modReports)), (dismissedFinal, len(modReportsDismissed)))

    def parseUsernotes(self, subredditUsernotes, user):
        submission = None
        comment = None
        link = ""
        usernoteStringLink = "[{}] [{}]({}) - by /u/{} - {}\n"
        usernoteString = "[{}] {} - by /u/{} - {}\n"
        final = ""
        notes = subredditUsernotes.getUsernotes(user)
        mods = notes[1]
        warnings = notes[2]
        colors = subredditUsernotes.getUsernoteWarningColor()
        if 'ns' in notes[0]:
            for note in notes[0]['ns']:
                w = colors[warnings[note["w"]]][0]
                n = note["n"]
                l = note["l"]
                m = mods[note["m"]]
                t = timeago.format(datetime.datetime(*time.localtime(note['t'])[:6]))
                if len(l) == 0:
                    final += usernoteString.format(w, n, m, t)
                elif len(l) == 8:
                    if l[0] == "l":
                        lstr = l.split(',')
                        submission = self.reddit.submission(lstr[1])
                        link = submission.shortlink
                        final += usernoteStringLink.format(w, n, link, m, t)
                    elif l[0] == "m":
                        link = "https://www.reddit.com/message/messages/" + l.split(',')[1]
                        final += usernoteStringLink.format(w, n, link, m, t)
                if len(l) == 15 and l[0] == 'l' :
                    comment = self.reddit.comment(lstr[2])
                    commentid = comment.id
                    submission = comment.submission
                    link = "https://www.reddit.com{}{}".format(submission.permalink, commentid)
                    final += usernoteStringLink.format(w, n, link, m, t)
        else:
            return
        if len(final) == 0:
            return
        else:
            return final
 
class Usernotes:
    
    def __init__(self, reddit: praw.Reddit, subreddit: praw.reddit.models.Subreddit):
        """Initialize a Usernote instance.
            Parameters
            ----------
            reddit: praw.Reddit
                Reddit instance
            subreddit: praw.reddit.models.Subreddit
                Subreddit object you want usernotes from
        """
        self.reddit = reddit
        self.subreddit = subreddit
        
    def getUsernoteWarningColor(self):
        sub = self.subreddit
        wikiPage = sub.wiki["toolbox"]
        try:
            wikiPage._fetch()
            content = json.loads(wikiPage.content_md)
            usernoteColorsDict = {}
            for note in content['usernoteColors']:
                usernoteColorsDict[note['key']] = [note['text'], note['color']]
            return usernoteColorsDict
        except:
            return

    def getUsernotes(self, *args):
        """Returns Usernotes, mods, and note types,

            Returns
            -------
            ([usernotes], mods: [str], warning types: [str])


            Structure of usernotes
            ----------------------
            User object structure
            
            ns: A list of note objects on a user, short for "notes"

            Note object structure

            n: The note text, short for "note"
            l: The thing information to which the note links, short for "link"
            t: The time the note was made in seconds (schema 4 uses milliseconds), short for "time"
            m: An index from the users constants array, short for "mod"
            w: An index from the warnings constants array, short for "warning" ("type" used internally)

            {
                "redditor": {
                    "ns": [
                        {
                            "n": "asking for updoots",
                            "t": 1430842947,
                            "m": 0,
                            "l": "l,2oaecb",
                            "w": 0
                        }
                    ]
                },
                "redditor2": {
                    "ns": [
                        {
                            "n": "asking for downdoots",
                            "t": 1430856730,
                            "m": 1,
                            "l": "l,25kvck",
                            "w": 0
                        }
                    ]
                }
            }
        """
        sub = self.subreddit
        wikiPage = sub.wiki["usernotes"]
        wikiPage._fetch()
        content = json.loads(wikiPage.content_md)
        if not content["ver"] == 6:
            raise Exception("Usernotes version 5 is not supported. Please update your usernotes to version 6.")
        mods = content["constants"]["users"]
        warningTypes = content["constants"]["warnings"]
        blob = content["blob"]
        decodedBase64 = base64.b64decode(blob)
        if args:
            if args[0] in json.loads(zlib.decompress(decodedBase64).decode("utf-8")):
                return [json.loads(zlib.decompress(decodedBase64).decode("utf-8"))[args[0]], mods, warningTypes]
            else:
                return [json.loads(zlib.decompress(decodedBase64).decode("utf-8")), mods, warningTypes]
        else:
            return [json.loads(zlib.decompress(decodedBase64).decode("utf-8")), mods, warningTypes]
    
    def addUsernote(self, user: praw.reddit.models.Redditor, note: str, thing: Union[praw.reddit.models.Submission, praw.reddit.models.Comment, praw.reddit.models.ModmailConversation, str, None], subreddit: praw.reddit.models.Subreddit, warningType: str):
        """Adds an usernote, to the selected subreddit and automatically saves it to wiki page.

            Parameters
            ----------
            user: praw.reddit.models.Redditor
                User that your adding the note to
            note: str
                Note
            thing: one of: praw.reddit.models.Submission, praw.reddit.models.Comment, praw.reddit.models.ModmailConversation
                the thing the note is referencing
            subreddit: praw.reddit.models.Subreddit
                Subreddit object you want add the usernote to
            warningType: str
                type of note
                spaces are represented as `_`
                e.g., `"abusewarning"`
                THIS IS CASE SENSITIVE
            Returns
            -------
            nothing
        """
        mod = self.reddit.user.me()
        
        if user == None:
            raise Exception("User deleted account")
        if not mod in subreddit.moderator():
            raise Exception("Current authencated user, {}, is not a moderator of {}".format(mod, subreddit.display_name))
        if not "wiki" in subreddit.moderator.PERMISSIONS:
            raise Exception("Current authencated user, {}, does not have Wiki permissions on {}".format(mod, subreddit.display_name))
        
        data = self.getUsernotes()
        notes = data[0]
        mods = data[1]
        modsUpdated = False
        warningTypes = data[2]
        if not mod.name in mods:
            mods.append(mod.name)
            modsUpdated = True
        if not warningType in warningTypes:
            raise Exception("Warning type, {}, not found usernote warning list".format(warningType))
        userNotes = None
        if user.name == "[deleted]":
            raise Exception("User deleted account")
        if user.name in notes:
            userNotes = notes[user.name]
        else:
            notes[user.name] = {"ns": []}
            userNotes = notes[user.name]
        l = ""
        m = mods.index(mod)
        n = note
        t = round(time.time())
        w = warningTypes.index(warningType)
        if isinstance(thing, praw.reddit.models.Submission):
            l = "l,{}".format(thing.id)
        elif isinstance(thing, praw.reddit.models.Comment):
            l = "l,{},{}".format(thing.submission.id, thing.id)
        elif isinstance(thing, praw.reddit.models.ModmailConversation):
            l = "https://mod.reddit.com/mail/perma/{}".format(thing.id)
        elif isinstance(thing, str):
            l = thing
        newUsernote = {"l": l, "m": m, "n": n, "t": t, "w": w}
        userNotes["ns"].insert(0, newUsernote)
        data[0][user.name] = userNotes
        if modsUpdated:
            self.__saveUsernotes(data[0], user.name, mods)
        else:
            self.__saveUsernotes(data[0], user.name)

    def __saveUsernotes(self, data: list, user: str, *mods: list):
        sub = self.subreddit
        wikiPage = sub.wiki["usernotes"]
        wikiPage._fetch()
        content = json.loads(wikiPage.content_md)
        jsonDump = json.dumps(data, separators=(",", ":"))
        compressedBlob = zlib.compress(jsonDump.encode("utf-8"), -1)
        newBlob = base64.encodebytes(compressedBlob)
        finalOutput = ""
        for line in newBlob.decode().splitlines():
            finalOutput += line
        content["blob"] = finalOutput
        if mods:
            content["constants"]["users"] = mods
        content_md = json.dumps(content, separators=(",", ":"))
        wikiPage.edit(content=content_md, reason='"create new note on user {}" via Bot Usernote Module by /u/Lil_SpazJoekp'.format(user))
        return finalOutput
