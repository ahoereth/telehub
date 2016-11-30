from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from lib.utils import pick, sgpl, markdown_link as link


class GitHubEventResponder:
    def __init__(self, event, payload):
        self.event = event
        self.payload = payload
        self.repo = self._parse_repository(payload['repository'])
        self.sender = self._parse_sender(payload['sender'])

    def get_message(self):
        if hasattr(self, self.event):
            msg = getattr(self, self.event)()
            msg = {'text': msg} if isinstance(msg, str) else msg
            return dict({
                'parse_mode': 'Markdown',
                'disable_web_page_preview': True,
            }, **msg)
        else:
            return None

    def _parse_sender(self, raw):
        sender = pick(raw, 'login', 'html_url')
        sender['text'] = link(raw['login'], raw['html_url'])
        return sender

    def _parse_repository(self, raw):
        repo = pick(raw, 'full_name', 'name', 'html_url', 'default_branch')
        repo['text'] = link(raw['full_name'], raw['html_url'])
        return repo

    def _cta(self, text, url):
        return InlineKeyboardMarkup(
            [[InlineKeyboardButton(text, url)]]
        )

    def _repo_action(self, text):
        return '{}: {}'.format(self.repo['text'], text)

    def _user_action(self, text):
        return '{} {}'.format(self.sender['text'], text)

    def _createdelete_action(self, action, reftype, ref):
        return self._repo_action(self._user_action('{} {} `{}`.'.format(
            action, reftype, ref,
        )))

    def _post_action(self, action, posttype, title, message, url):
        return self._repo_action(self._user_action('{} {} _{}_: _{}_'.format(
            action,
            posttype,
            title,
            message,
        )))

    def _comment_action(self, posttype, data):
        return self._post_action(
            'commented on',
            posttype,
            link(data['title'], data['html_url']),
            data['body'][:255] + ' [...]' if len(data['body']) > 255 else '',
        )

    def push(self):
        # forced = d['forced']
        return self._repo_action(self._user_action(
            'pushed {} to branch `{}`.'.format(
                sgpl(len(self.payload['commits']), 'commit', 'commits'),
                self.payload['ref'].replace('refs/heads/', ''),
            )
        ))

    def create(self):
        return self._createdelete_action(
            'created',
            self.payload['ref_type'],
            self.payload['ref'],
        )

    def delete(self):
        return self._createdelete_action(
            'deleted',
            self.payload['ref_type'],
            self.payload['ref'],
        )

    def gollum(self):
        return self._post_action(
            self.payload['pages'][0]['action'],
            self.payload['pages'][0]['title'],
            self.payload['pages'][0]['summary'],
            self.payload['pages'][0]['html_url'],
        )

    def issue(self):
        data = self.payload['issue'],
        return self._post_action(
            'created',
            'issue',
            data['title'],
            data['body'][:255] + ' [...]' if len(data['body']) > 255 else '',
            data['html_url'],
        )

    def pull_request(self):
        data = self.payload['pull_request']
        return self._post_action(
            'created',
            'pull request',
            data['title'],
            data['body'][:255] + ' [...]' if len(data['body']) > 255 else '',
            data['html_url'],
        )

    def issue_comment(self):
        return self._comment_action('issue', dict({
            'title': '#' + self.payload['issue']['number'],
        }, **pick(self.payload['comment'], 'html_url', 'body')))

    def commit_comment(self):
        return self._comment_action(dict({
            'title': self.payload['comment']['commit_id'][:7]
        }, **pick(self.payload['comment'], 'html_url', 'body')))

    def fork(self):
        return self._user_action('forked {}'.format(
            self.sender['text'],
            self.repo['text'],
        ))

    def member(self):
        member = self.payload['member']
        return self._repo_action('{} was added as a collaborator.'.format(
            link(member['login'], member['html_url']),
        ))

    def milestone(self):
        milestone = self.payload['stone']
        return self._repo_action(self._user_action(('{} milestone {}'.format(
            self.payload['action'],
            link(milestone['title'], milestone['html_url'])
        ))))

    def public(self):
        return {
            'text': '{} made {} public!'.format(
                self.sender['text'],
                self.repo['text'],
            ),
            'reply_markup': self._cta('View Repository', self.repo['url']),
        }

    def ping(self):
        return 'I just received a ping from {}.'.format(self.repo['text'])
