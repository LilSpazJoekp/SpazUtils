"""Provides a way of automating ToolBox's User Notes for Reddit"""
import time, praw, json, base64, zlib, prawcore, logging
from typing import Union
from .info import __version__

log = logging.getLogger(__package__)

class Usernotes:

    __all__ = ['getUsernotes', 'addUsernote', 'getUsernoteWarningColor', 'pruneDeleted']

    def __init__(self, reddit: praw.Reddit, subreddit: praw.reddit.models.Subreddit):
        '''Initialize a Usernote instance.
            Parameters
            ----------
            :param: praw.Reddit
                Reddit instance
            subreddit: praw.reddit.models.Subreddit
                Subreddit object you want usernotes from
        '''
        self.reddit = reddit
        if isinstance(subreddit, str):
            subreddit = reddit.subreddit(subreddit)
        self.subreddit = subreddit

    def getUsernoteWarningColor(self):
        sub = self.subreddit
        wikiPage = sub.wiki['toolbox']
        try:
            wikiPage._fetch()
            content = json.loads(wikiPage.content_md)
            usernoteColorsDict = {}
            for note in content['usernoteColors']:
                usernoteColorsDict[note['key']] = [note['text'], note['color']]
            return usernoteColorsDict
        except:
            return

    def getUsernotes(self, user=None):
        '''Returns Usernotes, mods, and note types,

            Attributes
            ----------

            user: str
                user to fetch from usernotes

            Returns
            -------
            ([usernotes], mods: [str], warning types: [str])

            Structure of usernotes
            ----------------------
            User object structure

            ns: A list of note objects on a user, short for 'notes'

            Note object structure

            n: The note text, short for 'note'
            l: The thing information to which the note links, short for 'link'
            t: The time the note was made in seconds (schema 4 uses milliseconds), short for 'time'
            m: An index from the users constants array, short for 'mod'
            w: An index from the warnings constants array, short for 'warning' ('type' used internally)

            {
                'redditor': {
                    'ns': [
                        {
                            'n': 'asking for updoots',
                            't': 1430842947,
                            'm': 0,
                            'l': 'l,2oaecb',
                            'w': 0
                        }
                    ]
                },
                'redditor2': {
                    'ns': [
                        {
                            'n': 'asking for downdoots',
                            't': 1430856730,
                            'm': 1,
                            'l': 'l,25kvck',
                            'w': 0
                        }
                    ]
                }
            }
        '''
        sub = self.subreddit
        wikiPage = sub.wiki['usernotes']
        try:
            wikiPage._fetch()
        except prawcore.NotFound:
            raise prawcore.NotFound('usernotes wiki page was not found, please create it with toolbox first.')
        content = json.loads(wikiPage.content_md)
        if not content['ver'] == 6:
            raise Exception('Usernotes version 5 is not supported. Please update your usernotes to version 6.')
        mods = content['constants']['users']
        warningTypes = content['constants']['warnings']
        blob = content['blob']
        decodedBase64 = base64.b64decode(blob)
        notesStr = zlib.decompress(decodedBase64).decode('utf-8')
        for i, m in enumerate(mods):
            notesStr = notesStr.replace(f'"m":{i},', f'"m":"{m}",')
        for i, w in enumerate(warningTypes):
            if w:
                notesStr = notesStr.replace(f'"w":{i}{"}"}', f'"w":"{w}"{"}"}')
            else:
                notesStr = notesStr.replace(f'"w":{i}{"}"}', f'"w":null{"}"}')
        notes = json.loads(notesStr)
        if user:
            try:
                if isinstance(user, str):
                    user = self.reddit.redditor(user)
                user._fetch()
            except prawcore.NotFound:
                raise prawcore.NotFound(f'User, {user}, either deleted their account or it does not exist.')
            if user.name in notes:
                return {user.name: notes[user.name]}
            else:
                return {}
        return notes

    def genConstants(self, notes):
        flatNotes = [(note['l'], user, note['t'], note['n'], note['m'], note['w']) for user in notes for note in notes[user]['ns']]
        flatNotes.sort(key=lambda k: k[2])
        mods = []
        warnings = []
        replacedNotes = []
        usernotes = {}
        for note in flatNotes:
            mod = note[4]
            warning = note[5]
            if not mod in mods:
                mods.append(mod)
            if not warning in warnings:
                warnings.append(warning)
            replacedNotes.append((note[0], note[1], note[2], note[3], mods.index(mod), warnings.index(warning)))
            usernotes[note[1]] = {'ns': []}
        for note in replacedNotes:
            usernotes[note[1]]['ns'].append({'l': note[0], 'm': note[4], 'n': note[3], 't': note[2], 'w': note[5]})
        return mods, warnings, usernotes

    def addUsernote(self, user: praw.reddit.models.Redditor, note: str, thing: Union[praw.reddit.models.Submission, praw.reddit.models.Comment, praw.reddit.models.ModmailConversation, str, None], warningType: str, mod: Union[praw.reddit.models.Redditor,str,None]):
        '''Adds an usernote, to the selected subreddit and automatically saves it to wiki page.

            Parameters
            ----------
            user: praw.reddit.models.Redditor
                User that your adding the note to
            note: str
                Note
            thing: one of: praw.reddit.models.Submission, praw.reddit.models.Comment, praw.reddit.models.ModmailConversation
                the thing the note is referencing
            warningType: str
                type of note
                spaces are represented as `_`
                e.g., `'abusewarning'`
                THIS IS CASE SENSITIVE
            Returns
            -------
            None
        '''

        try:
            if isinstance(mod, str):
                mod = self.reddit.redditor(mod)
            mod._fetch()
        except prawcore.NotFound:
            raise prawcore.NotFound(f'mod, {mod}, either deleted their account or it does not exist.')
        try:
            if isinstance(user, str):
                user = self.reddit.redditor(user)
            user._fetch()
        except prawcore.NotFound:
            raise prawcore.NotFound(f'User, {user}, either deleted their account or it does not exist.')
        finally:
            if getattr(user, 'is_suspended', None):
                raise Exception(f'User, {user} is currently suspended.')

        if not mod in self.subreddit.moderator():
            raise Exception(f'Current authencated user, {mod}, is not a moderator of {self.subreddit.display_name}')

        if not 'wiki' in self.subreddit.moderator.PERMISSIONS:
            raise Exception(f'Current authencated user, {mod}, does not have Wiki permissions on {self.subreddit.display_name}')

        notes = self.getUsernotes()
        warningTypes = self.getUsernoteWarningColor()
        if not warningType in warningTypes:
            raise Exception(f'Warning type, {warningType}, not found usernote warning list')
        if user.name in notes:
            userNotes = notes[user.name]
            new = False
        else:
            notes[user.name] = {'ns': []}
            userNotes = notes[user.name]
            new = True
        l = ''
        m = mod.name
        n = note
        t = round(time.time())
        w = warningType
        if isinstance(thing, praw.reddit.models.Submission):
            l = f'l,{thing.id}'
        elif isinstance(thing, praw.reddit.models.Comment):
            l = f'l,{thing.submission.id},{thing.id}'
        elif isinstance(thing, praw.reddit.models.ModmailConversation):
            l = f'https://mod.reddit.com/mail/perma/{thing.id}'
        elif isinstance(thing, str):
            l = thing
        newUsernote = {'l': l, 'm': m, 'n': n, 't': t, 'w': w}
        userNotes['ns'].insert(0, newUsernote)
        notes[user.name] = userNotes
        self.__saveUsernotes(*self.genConstants(notes), user, new)

    def __saveUsernotes(self, mods, warnings, notes, user, new=False):
        sub = self.subreddit
        wikiPage = sub.wiki['usernotes']
        jsonDump = json.dumps(notes, separators=(',', ':'))
        compressedBlob = zlib.compress(jsonDump.encode('utf-8'), -1)
        newBlob = base64.encodebytes(compressedBlob)
        finalOutput = ''
        for line in newBlob.decode().splitlines():
            finalOutput += line
        payload = {"ver":6,"constants":{"users":mods,"warnings":warnings},"blob":finalOutput}
        log.debug(payload)
        content_md = json.dumps(payload, separators=(',', ':'))
        if new:
            wikiPage.edit(content=content_md, reason=f'"create new note on new user {user}" via Bot Usernote Module v{(__version__ or "0.0.a")} by /u/Lil_SpazJoekp')
        else:
            wikiPage.edit(content=content_md, reason=f'"create new note on user {user}" via Bot Usernote Module v{(__version__ or "0.0.a")} by /u/Lil_SpazJoekp')
        log.info(f'Created usernote on user')
        return finalOutput

    def pruneDeleted(self, olderThan: int=None):
        notes = self.getUsernotes()
        reddit = self.reddit
        removeList = []
        users = notes[0]
        totalCount = len(users)
        padding = len(str(totalCount))
        for i, user in enumerate(users, 1):
            redditor = reddit.redditor(user)
            log.info(f'{str(i).zfill(padding)}/{str(totalCount).zfill(padding)} :: Checking u/{user}')
            try:
                redditor._fetch()
            except prawcore.NotFound as error:
                log.exception(error)
                removeList.append(user)
