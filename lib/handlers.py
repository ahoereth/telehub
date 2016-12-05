from telegram import ReplyKeyboardMarkup

from .db import db
from .logger import logger


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def start(bot, update):
    msg = """ \
Hello {}!
I can send you or a group you add me to notifications about activity
on specified GitHub repos. I will notify you about new commits,
issues and comments.
    """.format(update.message.from_user.first_name)
    update.message.reply_text(msg, parse_mode='Markdown')


def showhelp(bot, update):
    msg = """ \
I can send you or a group you add me to notifications about activity
on specified GitHub repos. I will notify you about new commits,
issues and comments.

1. Go to your repositorie's `settings`
2. Select `Webhooks` and then the `add webhook` button in the top right
    *Payload URL*: `https://telegit.vega.uberspace.de/`
    *Content type*: `application/json`
    *Secret*: Something secret -- we will need it later!
    *Events*: For information on which events I can handle, type `/events`.
    *Activity*: Checked!
3. Send me a message with `/subscribe <username>/<repo> <secret>`

To stop me from watching a repo for you, use `/unsubscribe <username>/<repo>`
    """
    update.message.reply_text(msg, parse_mode='Markdown')


def subscribe(bot, update, args, chat_data):
    if len(args) != 2:
        return update.message.reply_text(
            'Please pass a repository '
            '(as `username/repository` string) and the webhook secret.',
            parse_mode='Markdown',
        )

    repo, secret = args
    db.add(repo, update.message.chat.id, secret)

    msg = (
        "I will now notify you about events from {}. Make sure you "
        "configured a webhook for sending events to "
        "`https://telegit.vega.uberspace.de/`. For information on "
        "how to do so type `/help`."
    )

    update.message.reply_text(msg.format(repo), parse_mode='Markdown')


def unsubscribe(bot, update, args, chat_data):
    if len(args) != 1:
        return update.message.reply_text(
            'Please pass a repository (as `username/repository` string).',
            parse_mode='Markdown',
        )

    repo = args[0]
    db.remove(repo, update.message.chat.id)
    msg = (
        'Okay, I won\'t notify you about activity in the repository '
        '`{}` anymore.'
    )
    update.message.reply_text(msg.format(repo), parse_mode='Markdown')
