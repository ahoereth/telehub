from telegram.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram.inlinekeyboardbutton import InlineKeyboardButton
from lib.utils import pick, sgpl, markdown_link


class GitHubEventResponder:
    def __init__(self, event, payload):
        self.event = event
        self.forced = payload['forced']
        self.compare_url = payload['compare']
        self.commits = payload['commits']
        self.repo = self._parse_repository(payload['repository'])
        self.pusher = self._parse_pusher(payload['pusher'], payload['sender'])

    def _parse_pusher(self, pusher, sender):
        if pusher['name'] == sender['login']:
            return dict({
                'url': sender['html_url'],
                'text': markdown_link(pusher['name'], sender['html_url']),
            }, **pusher)
        else:
            return dict({'text': pusher['name']}, **pusher)

    def _parse_repository(self, raw):
        repo = pick(raw, 'full_name', 'name', 'url', 'default_branch')
        repo['text'] = markdown_link(raw['full_name'], raw['url'])
        return repo

    def _cta(self, text, url):
        return InlineKeyboardMarkup(
            [[InlineKeyboardButton(text, url)]]
        )

    def push(self, compareButton=True):
        text = '{} pushed {} to {}.'.format(
            self.pusher['text'],
            sgpl(len(self.commits), 'commit', 'commits'),
            self.repo['text'],
        )
        action = self._cta('View Changes', self.compare_url)
        return {'text': text, 'reply_markup': action}
