"""Provides automated flair removal with: usernotes, commenting, and other mod actions, and logging said actions to a Discord channel"""
import time, praw, json, datetime, timeago, requests, zlib, string, logging, psycopg2, os
from discord import embeds
from .usernotes import Usernotes
from .utils import logStream

log = logging.getLogger(__package__)
log.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(name)s :: %(levelname)s :: %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)

thingTypes = {'t1': 'comment', 't4': 'message', 't2': 'redditor', 't3': 'submission', 't5': 'subreddit', 't6': 'trophy'}

class FlairRemoval:

    __all__ = ['checkModAction', 'logStream']

    def __init__(self, reddit: praw.Reddit, subreddit: praw.reddit.models.Subreddit, webhook: str, flairList: dict, botName: str, sql: psycopg2.extensions.cursor, slack=False, slackChannel=None, webhookEnabled=True):
        """
        Initialized FlairRemoval Class

        :param reddit: reddit instance
        :param subreddit: subreddit object
        :param webhook: webhook url to send removal notifications can be discord or slack. If slack set slack params.
        :param flairList:  of flairs
        :param botName: name of bot. Schema name depends on this.
        :param sql: psycopg2 cursor object
        :param slack: set true to use slack
        :param slackChannel: channel for slack webhook

        """
        self.reddit = reddit
        self.subreddit = subreddit
        self.webhook = webhook
        self.flairList = flairList
        self.botName = botName or self.reddit.user.me().name
        self.sql = sql
        self.slack = slack
        self.slackChannel = slackChannel
        self.webhookEnabled = webhookEnabled

    def logStream(self):
        return logStream(self.subreddit.mod.log, pause_after=0)

    def __parseModAction(self, action: praw.models.ModAction, flair: str):
        sqlStr = f'''INSERT INTO {self.botName}.flairlog(id, created_utc, moderator, target_author, target_body, target_id, target_permalink, target_title, flair) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO UPDATE SET created_utc=EXCLUDED.created_utc returning *,case when xmax::text::int > 0 then \'alreadyRemoved\' else \'inserted\' end,ctid;'''
        id = (getattr(action, 'id', None).split('_')[1] if getattr(action, 'id', None) else None)
        created_utc = getattr(action, 'created_utc', None)
        moderator = getattr(action, '_mod', None)
        target_author = getattr(action, 'target_author', None)
        target_fullname = getattr(action, 'target_fullname', None)
        targe_type = None
        target_id = None
        if target_fullname:
            targe_type, target_id = (thingTypes[target_fullname.split('_')[0]], target_fullname.split('_')[1])
        target_body = getattr(action, 'target_body', None)
        target_permalink = getattr(action, 'target_permalink', None)
        target_title = getattr(action, 'target_title', None)
        data = (
            id,
            datetime.datetime.utcfromtimestamp(action.created_utc).replace(tzinfo=datetime.timezone.utc),
            moderator,
            target_author,
            target_id,
            target_body,
            target_permalink,
            target_title,
            flair
            )
        return (sqlStr, data)

    def __genDateString(self, epoch=time.localtime(), gmtime=False, format='%B %d, %Y at %I:%M:%S %p %Z'):
        if not gmtime:
            return time.strftime(format, time.localtime(epoch))
        else:
            return time.strftime(format, time.gmtime(epoch))

    def checkModAction(self, modAction: praw.models.ModAction):
        if modAction and modAction.action == 'editflair' and modAction.target_fullname and modAction.target_fullname[:2] == "t3":
            submission = self.reddit.submission(id=modAction.target_fullname[3:])
            try:
                if hasattr(submission, 'link_flair_text') and submission.link_flair_text:
                    submissionFlair = submission.link_flair_text.lower()
                else:
                    submissionFlair = ''
                query = self.__parseModAction(modAction, submissionFlair)
                log.debug('Checking if in flair list')
                if submissionFlair in self.flairList:
                    print(f'Found flair: {submissionFlair} by {modAction._mod} at {self.__genDateString(modAction.created_utc, format="%m/%d/%Y %I:%M:%S %p")}')
                    try:
                        print('Checking if already actioned')
                        self.sql.execute(*query)
                        results = self.sql.fetchone()
                        alreadyRemoved = results[[i for i, column in enumerate(self.sql.description) if column.name == 'case'][0]] == 'alreadyRemoved'
                        if alreadyRemoved:
                            print(f'Already Removed {submission.shortlink} by {getattr(submission.author, "name", "[deleted]")} with {submissionFlair} flair, Mod: {modAction._mod}')
                        else:
                            try:
                                actionParam = self.flairList[submissionFlair]
                                print('Removing')
                                self.__action(submission, actionParam, modAction)
                                print(f'Successfully removed {submission.shortlink} by {getattr(submission.author, "name", "[deleted]")} with {submissionFlair} flair, Mod: {modAction._mod}')
                            except Exception as error:
                                log.exception(error)
                                pass
                    except psycopg2.IntegrityError as error:
                        log.exception(error)
                        pass
            except Exception as error:
                log.exception(error)
                pass

    def __action(self, submission: praw.models.reddit.submission.Submission, action: dict, modAction: praw.models.ModAction, testing=False):
        if not testing:
            submission.mod.remove()
            try:
                if 'ban' in action:
                    self.__setBan(submission, action['ban'])
                if 'lock' in action:
                    submission.mod.lock()
                if 'commentReply' in action:
                    comment = submission.reply(action['commentReply'].format(author=getattr(submission.author, 'name', '[deleted]'), subreddit=submission.subreddit, kind=thingTypes[submission.fullname[:2]], domain=submission.domain, title=submission.title, url=submission.shortlink))
                    comment.mod.distinguish(how='yes', sticky=True)
                    comment.mod.approve()
                if 'usernote' in action:
                    usernote = action['usernote']
                    subredditUsernotes = Usernotes(reddit=self.reddit, subreddit=submission.subreddit)
                    subredditUsernotes.addUsernote(user=submission.author, note=usernote['usernote'], thing=submission, warningType=usernote['usernoteWarningType'])
            except Exception as error:
                log.error(error)
        if self.webhookEnabled:
            if self.slack:
                data = self.__generateSlackEmbed(submission, action, modAction)
            else:
                data = {'embeds': self.__generateEmbed(submission, action, modAction)}
            log.debug(data)
            requests.post(self.webhook, json=data)

    def __generateEmbed(self, submission: praw.models.reddit.submission.Submission, params: dict, modAction: praw.models.ModAction):
        embed = embeds.Embed(title='Bot Removal Notification', url=submission.shortlink, description=params['description'])
        if not submission.is_self:
            embed.set_image(url=submission.url)
        embed.add_field(name='Submission:', value=f'[{submission.title}]({submission.shortlink})', inline=False)
        if submission.author:
            embed.add_field(name='Author:', value=f'[{submission.author.name}](https://reddit.com/user/{submission.author.name})')
        else:
            embed.add_field(name='Author:', value='[deleted]')
        embed.add_field(name='Posted At:', value=time.strftime('%b %d, %Y %I:%M %p %Z', time.gmtime(submission.created_utc)))
        embed.add_field(name='Score:', value=f'{submission.score:,}')
        embed.add_field(name='Comments:', value=f'{submission.num_comments:,}')
        embed.add_field(name='Removed By:', value=f'{modAction._mod}')
        if 'ban' in params:
            duration = self.__checkBanDuration(params['ban'])
            if duration:
                if duration > 1:
                    embed.add_field(name='Ban Duration:', value=f'{duration:,} days')
                else:
                    embed.add_field(name='Ban Duration:', value=f'{duration:,} day')
            else:
                embed.add_field(name='Ban Duration:', value='Permanent')
        modReports = self.__parseModReports(submission)
        if modReports:
            if not modReports[0][1] == 0:
                embed.add_field(name=f'Mod Reports ({modReports[0][1]:,}):', value=modReports[0][0])
            if not modReports[1][1] == 0:
                embed.add_field(name=f'Mod Reports Dismissed ({modReports[1][1]:,}):', value=modReports[1][0])
        userReports = self.__parseUserReports(submission)
        if userReports:
            if not userReports[0][1] == 0:
                embed.add_field(name=f'User Reports ({userReports[0][1]:,}):', value=userReports[0][0])
            if not userReports[1][1] == 0:
                embed.add_field(name=f'User Reports Dismissed ({userReports[1][1]:,}):', value=userReports[1][0])
        usernotesString = None
        if submission.author:
            usernotesString = self.__parseUsernotes(Usernotes(reddit=self.reddit, subreddit=submission.subreddit), submission.author.name)
        if usernotesString:
            embed.add_field(name='Usernotes:', value=usernotesString, inline=False)
        embed.set_footer(text=time.strftime('%B %d, %Y at %I:%M:%S %p %Z', time.gmtime()))
        return [embed.to_dict()]

    def __slackEmbedField(self, name, value, inline=True):
        return {"title": name, "value": value, "short": inline}

    def __generateSlackEmbed(self, submission: praw.models.reddit.submission.Submission, params: dict, modAction: praw.models.ModAction):

        attachment = {
            "mrkdwn_in": ["text", "fields", "value"],
            "color": "#36a64f",
            "title": "Bot Removal Notification",
            "title_link": submission.shortlink,
            "text": params['description'],
            "fields": [],
            "ts": time.gmtime()
        }
        if not submission.is_self:
            attachment['thumb_url'] = submission.url
        attachment['fields'].append(self.__slackEmbedField(name='Submission:', value=f'<{submission.shortlink}|{submission.title}>', inline=False))
        if submission.author:
            attachment['author_name'] = submission.author.name
            attachment['author_link'] = f'https://reddit.com/user/{submission.author.name}'
            attachment['author_icon'] = submission.author.icon_img
        else:
            attachment['author_name'] = '[deleted]'
        attachment['fields'].append(self.__slackEmbedField(name='Posted At:', value=time.strftime('%b %d, %Y %I:%M %p %Z', time.gmtime(submission.created_utc))))
        attachment['fields'].append(self.__slackEmbedField(name='Score:', value=f'{submission.score:,}'))
        attachment['fields'].append(self.__slackEmbedField(name='Comments:', value=f'{submission.num_comments:,}'))
        attachment['fields'].append(self.__slackEmbedField(name='Removed By:', value=f'{modAction._mod}'))
        if 'ban' in params:
            duration = self.__checkBanDuration(params['ban'])
            if duration:
                if duration > 1:
                    attachment['fields'].append(self.__slackEmbedField(name='Ban Duration:', value=f'{duration:,} days'))
                else:
                    attachment['fields'].append(self.__slackEmbedField(name='Ban Duration:', value=f'{duration:,} day'))
            else:
                attachment['fields'].append(self.__slackEmbedField(name='Ban Duration:', value='Permanent'))
        modReports = self.__parseModReports(submission)
        if modReports:
            if not modReports[0][1] == 0:
                attachment['fields'].append(self.__slackEmbedField(name=f'Mod Reports ({modReports[0][1]:,}):', value=modReports[0][0]))
            if not modReports[1][1] == 0:
                attachment['fields'].append(self.__slackEmbedField(name=f'Mod Reports Dismissed ({modReports[1][1]:,}):', value=modReports[1][0]))
        userReports = self.__parseUserReports(submission)
        if userReports:
            if not userReports[0][1] == 0:
                attachment['fields'].append(self.__slackEmbedField(name=f'User Reports ({userReports[0][1]:,}):', value=userReports[0][0]))
            if not userReports[1][1] == 0:
                attachment['fields'].append(self.__slackEmbedField(name=f'User Reports Dismissed ({userReports[1][1]:,}):', value=userReports[1][0]))
        usernotesString = None
        if submission.author:
            usernotesString = self.__parseUsernotes(Usernotes(reddit=self.reddit, subreddit=submission.subreddit), submission.author.name)
        if usernotesString:
            attachment['fields'].append(self.__slackEmbedField(name='Usernotes:', value=usernotesString, inline=False))
        return {"channel": self.slackChannel, "attachments": [attachment]}

    def __checkBanDuration(self, banParams):
        if 'duration' in banParams:
            banNum = int(''.join(['0']+[letter for letter in str(banParams['duration']) if letter in string.digits]))
            if banNum > 0:
                return banNum
            else:
                return None
        else:
            return None

    def __setBan(self, submission: praw.models.Submission, params: dict):
        duration = self.__checkBanDuration(params)
        ban_message = params.get('ban_message')
        if ban_message:
            ban_message = ban_message.format(author=getattr(submission.author, 'name', '[deleted]'), subreddit=submission.subreddit, kind=thingTypes[submission.fullname[:2]], domain=submission.domain, title=submission.title, url=submission.shortlink)
        self.subreddit.banned.add(submission.author, duration=duration, ban_reason=params.get('ban_reason'), ban_message=ban_message, note=params.get('ban_note'))

    def __parseUserReports(self, submission: praw.models.reddit.submission.Submission):
        userReports = []
        userReportsDismissed = []
        userReports = submission.user_reports
        if 'user_reports_dismissed' in vars(submission):
            for dismissedReport in submission.user_reports_dismissed:
                userReportsDismissed.append(dismissedReport)
        reportString = '{0[1]}: {0[0]}\n'
        final = ''
        for report in userReports:
            final += reportString.format(report)
        dismissedFinal = ''
        for report in userReportsDismissed:
            dismissedFinal += reportString.format(report)
        if len(final) == 0 and len(dismissedFinal) == 0:
            return
        else:
            return ((final, len(userReports)), (dismissedFinal, len(userReportsDismissed)))

    def __parseModReports(self, submission: praw.models.reddit.submission.Submission):
        modReports = []
        modReportsDismissed = []
        modReports = submission.mod_reports
        if 'mod_reports_dismissed' in vars(submission):
            for dismissedReport in submission.mod_reports_dismissed:
                modReportsDismissed.append(dismissedReport)
        reportString = '{0[1]}: {0[0]}\n'
        final = ''
        for report in modReports:
            final += reportString.format(report)
        dismissedFinal = ''
        for report in modReportsDismissed:
            dismissedFinal += reportString.format(report)
        if len(final) == 0 and len(dismissedFinal) == 0:
            return
        else:
            return ((final, len(modReports)), (dismissedFinal, len(modReportsDismissed)))

    def __parseUsernotes(self, subredditUsernotes, user):
        submission = None
        comment = None
        link = ''
        usernoteStringLink = '[{}] [{}]({}) - by /u/{} - {}\n'
        usernoteString = '[{}] {} - by /u/{} - {}\n'
        final = ''
        notes = subredditUsernotes.getUsernotes(user)
        colors = subredditUsernotes.getUsernoteWarningColor()
        if user in notes and 'ns' in notes[user]:
            for note in notes[user]['ns']:
                w = colors[note['w']][0]
                n = note['n']
                l = note['l']
                m = note['m']
                t = timeago.format(datetime.datetime(*time.localtime(note['t'])[:6]))
                if len(l) == 0:
                    final += usernoteString.format(w, n, m, t)
                elif len(l) == 8:
                    if l[0] == 'l':
                        lstr = l.split(',')
                        submission = self.reddit.submission(lstr[1])
                        link = submission.shortlink
                        final += usernoteStringLink.format(w, n, link, m, t)
                    elif l[0] == 'm':
                        link = f'https://www.reddit.com/message/messages/{l.split(",")[1]}'
                        final += usernoteStringLink.format(w, n, link, m, t)
                if len(l) == 15 and l[0] == 'l' :
                    comment = self.reddit.comment(lstr[2])
                    commentid = comment.id
                    submission = comment.submission
                    link = f'https://www.reddit.com{submission.permalink}{commentid}'
                    final += usernoteStringLink.format(w, n, link, m, t)
        else:
            return
        if len(final) == 0:
            return
        else:
            return final