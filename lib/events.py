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
        text = '{} pushed {} to branch {} in {}.'.format(
            self.sender['text'],
            sgpl(len(self.payload['commits']), 'commit', 'commits'),
            self.payload['ref'].replace('/refs/heads/', ''),
            self.repo['text'],
        )
        action = self._cta('View Changes', self.payload['compare'])
        return {'text': text, 'reply_markup': action}

    def branchtag(self, action):
        text = '{} {} {} {} in {}.'.format(
            self.sender['text'],
            action,
            self.payload['ref_type'],
            self.payload['ref'],
            self.repo['text'],
        )
        return {'text': text}

    def create(self):
        return self.branchtag('created')

    def delete(self):
        return self.branchtag('deleted')

    def gollum(self):
        page = self.payload['pages'][0]
        text = '{} {} {} in {}: *{}*.'.format(
            self.sender['text'],
            page['action'],
            page['title'],
            self.repo['text'],
            page['summary'],
        )
        action = self._cta('View Page', page['html_url'])
        return {'text': text, 'reply_markup': action}

    def post(self, posttype, data):
        text = '{} created {} *{}* in {}: *{}*.'.format(
            self.sender['text'],
            posttype,
            data['title'],
            self.repo['text'],
            data['body'][:100] + ' [...]' if len(data['body']) > 100 else '',
        )
        action = self._cta('View %s' % posttype, data['html_url'])
        return {'text': text, 'reply_markup': action}

    def issue(self):
        return self.post('issue', self.payload['issue'])

    def pull_request(self):
        return self.post('pull request', self.payload['pull_request'])

    def issue_comment(self):
        issue = self.payload['issue']
        comment = self.payload['comment']
        body = comment['body']
        text = '{} commented on {}: *{}* in {}: *{}*.'.format(
            self.sender['text'],
            markdown_link('#' + issue['number'], issue['html_url']),
            body[:255] + ' [...]' if len(body) > 100 else '',
        )
        action = self._cta('View Comment', comment['html_url'])
        return {'text': text, 'reply_markup': action}
