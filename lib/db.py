import shelve


class DB:
    def __init__(self):
        self.shelf = shelve.open('subscriptions', writeback=True)

    def add(self, repo, chat_id, secret):
        if repo not in self.shelf:
            self.shelf[repo] = {}
        self.shelf[repo][chat_id] = secret
        self.shelf.sync()

    def remove(self, repo, chat_id):
        if repo in self.shelf:
            del self.shelf[repo]
        return True

    def get(self, repo):
        if repo not in self.shelf:
            return None
        return self.shelf[repo]


db = DB()
