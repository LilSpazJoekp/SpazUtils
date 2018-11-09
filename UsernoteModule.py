import praw, os, time, json, base64, zlib
from typing import Union
 
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
    
    # @staticmethod
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