from telegram.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram.inlinekeyboardbutton import InlineKeyboardButton
from lib.utils import pick, sgpl, markdown_link


class GitHubEventResponder:
    def __init__(self, event, payload):
        self.payload = payload
        self.event = event
        self.repo = self._parse_repository(payload['repository'])
        self.sender = self._parse_sender(payload['sender'])

    def get_message(self):
        if hasattr(self, self.event):
            return getattr(self, self.event)()
        else:
            return False

    def _parse_sender(self, raw):
        repo = pick(raw, 'login', 'html_url')
        repo['text'] = markdown_link(raw['login'], raw['html_url'])
        return repo

    def _parse_repository(self, raw):
        repo = pick(raw, 'full_name', 'name', 'url', 'default_branch')
        repo['text'] = markdown_link(raw['full_name'], raw['url'])
        return repo

    def _cta(self, text, url):
        return InlineKeyboardMarkup(
            [[InlineKeyboardButton(text, url)]]
        )

    def push(self):
        # forced = d['forced']
        text = '*{}*: {} pushed {} to branch `{}`.'.format(
            self.repo['text'],
            self.sender['text'],
            sgpl(len(self.payload['commits']), 'commit', 'commits'),
            self.payload['ref'].replace('refs/heads/', ''),
        )
        action = self._cta('View Changes', self.payload['compare'])
        return {'text': text, 'reply_markup': action}

    def action(self, action, tag, name):
        text = '*{}*: {} {} {} `{}`.'.format(
            self.repo['text'],
            self.sender['text'],
            action,
            actioned,
            name,
        )
        return {'text': text}

    def create(self):
        tag, name = self.payload['ref_type'], self.payload['ref']
        return self.act('created', tag, name)

    def delete(self):
        tag, name = self.payload['ref_type'], self.payload['ref']
        return self.act('deleted', tag, name)

    def gollum(self):
        page = self.payload['pages'][0]
        text = '*{}*: {} {} _{}_: _{}_'.format(
            self.repo['text'],
            self.sender['text'],
            page['action'],
            page['title'],
            page['summary'],
        )
        action = self._cta('View Page', page['html_url'])
        return {'text': text, 'reply_markup': action}

    def post(self, posttype, data):
        text = '*{}*: {} created {} _{}_: _{}_.'.format(
            self.repo['text'],
            self.sender['text'],
            posttype,
            data['title'],
            data['body'][:255] + ' [...]' if len(data['body']) > 255 else '',
        )
        action = self._cta('View %s' % posttype, data['html_url'])
        return {'text': text, 'reply_markup': action}

    def issue(self):
        return self.post('issue', self.payload['issue'])

    def pull_request(self):
        return self.post('pull request', self.payload['pull_request'])

    def comment(self, posttype, comment):
        body = comment['body']
        text = '*{}*: {} commented on {} {}: _{}_'.format(
            self.repo['text'],
            self.sender['text'],
            posttype,
            comment['title'],
            body[:255] + ' [...]' if len(body) > 255 else '',
        )
        action = self._cta('View Comment', comment['html_url'])
        return {'text': text, 'reply_markup': action}

    def issue_comment(self):
        issue = self.payload['issue']
        comment = self.payload['comment']
        return self.comment('issue', dict({
            'title': '#' + issue['number'],
        }, **pick(comment, 'html_url', 'body')))

    def commit_comment(self):
        return self.comment(dict({
            'title': comment['commit_id'][:7]
        }, **pick(comment, 'html_url', 'body')))

    def fork(self):
        text = '{} forked *{}*'.format(
            self.sender['text'],
            self.repo['text'],
        )
        return {'text': text}

    def member(self):
        member = self.payload['member']
        text = '*{}*: {} added {} as a collaborator.'.format(
            self.repo['text'],
            self.sender['text'],
            markdown_link(member['login'], member['html_url']),
        )
        return {'text': text}

    def milestone(self):
        stone = self.payload['stone']
        return self.act(
            action=self.payload['action'],
            tag='milestone',
            name=markdown_link(stone['title'], stone['html_url'])
        )

    def public(self):
        text = '{} made *{}* public'.format(
            self.sender['text'],
            self.repo['text'],
        )
        return {'text': text}
