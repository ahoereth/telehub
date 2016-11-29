from telegram import ReplyKeyboardMarkup

from lib.logger import logger
from lib.db import db


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def start(bot, update):
    msg = """ \
Hello {}!
I can send you or a group you add me to notifications about activity
on specified GitHub repos. I will notify you about new commits,
issues and comments.
    """.format(update.message.from_user.first_name)
    cta = ReplyKeyboardMarkup([['/help', '/addrepo']], one_time_keyboard=True)
    update.message.reply_text(
        msg,
        reply_markup=cta,
        parse_mode='Markdown',
    )


def showhelp(bot, update):
    msg = """ \
I can send you or a group you add me to notifications about activity
on specified GitHub repos. I will notify you about new commits,
issues and comments.

1. Go to your repositorie's `settings`
2. Select `Webhooks` and then the `add webhook` button in the top right
    *Payload URL*: `https://telegit.vega.uberspace.de/github`
    *Content type*: `application/json`
    *Secret*: Something secret -- we will need it later!
    *Events*: For information on which events I can handle, type `/events`.
    *Activity*: Checked!
3. Send me a message with `/addrepo <username>/<repo> <secret>`
    """
    update.message.reply_text(msg, parse_mode='Markdown')


def add_repo(bot, update, args, chat_data):
    if len(args) != 2:
        update.message.reply_text(
            'Please pass a repository '
            '(as `username/repository` string) and the webhook\' secret.'
        )
    repo, secret = args
    db[repo] = {
        'chat_id': update.message.chat.id,
        'secret': secret,
    }
    update.message.reply_text(
        'You will now receive notifications about {}.'.format(repo)
    )
