from telegram import ReplyKeyboardMarkup
from lib import logger, db


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def start(bot, update):
    msg = """ \
Hello {}!
I can send you or a group you add me to notifications about activity
on specified GitHub repos. I will notify you about new commits,
issues and comments.
    """.format(update.message.from_user.first_name)
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
    *Payload URL*: `https://telegit.vega.uberspace.de/`
    *Content type*: `application/json`
    *Secret*: Something secret -- we will need it later!
    *Events*: For information on which events I can handle, type `/events`.
    *Activity*: Checked!
3. Send me a message with `/subscribe <username>/<repo> <secret>`
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
    msg = """
I will now notify you about events from {}. Make sure you configured a webhook
for sending events to `https://telegit.vega.uberspace.de/`. For
information on how to do so type `/help`.
    """

    update.message.reply_text(msg.format(repo), parse_mode='Markdown')
