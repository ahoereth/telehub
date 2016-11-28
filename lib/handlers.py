from lib.logger import logger
from lib.db import db


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def start(bot, update):
    update.message.reply_text(
        'Hello {}'.format(update.message.from_user.first_name))


def add_repo(bot, update, args, chat_data):
    if len(args) != 2:
        update.message.reply_text('Please pass a repository (as \
            `username/repository` string) and the webhook\' secret.')
    repo, secret = args
    db[repo] = {
        'chat_id': update.message.chat.id,
        'secret': secret,
    }
    update.message.reply_text(
        'You will now receive notifications about {}.'.format(repo)
    )
