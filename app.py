#!/usr/bin/env python3
import os
import json
import hmac
from hashlib import sha1
from flask import Flask, request, abort
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler
from dotenv import load_dotenv, find_dotenv

from lib.db import db
from lib.logger import logger
from lib.events import GitHubEventResponder
from lib.handlers import error, start, add_repo


load_dotenv(find_dotenv())
URL = os.environ.get('URL')
PORT = os.environ.get('PORT')
TOKEN = os.environ.get('TOKEN')


app = Flask(__name__)
bot = Bot(os.environ.get('TOKEN'))
dispatcher = Dispatcher(bot, update_queue=None, workers=0)


def setup_bot():
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('addrepo', add_repo,
                           pass_args=True, pass_chat_data=True))
    dispatcher.add_error_handler(error)


@app.route('/%s' % os.environ.get('TOKEN'), methods=['POST'])
def webhook_handler():
    dispatcher.process_update(Update.de_json(request.json, bot))
    return 'ok'


@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    if bot.setWebhook('https://%s/%s' % (URL, TOKEN)):
        return 'webhook setup ok'
    else:
        abort(400, 'webhook setup failed')


@app.route('/github', methods=['POST'])
def github():
    headers = request.headers
    # raw = request.data
    payload = request.json
    repository = payload['repository']['full_name']

    if repository not in db:
        abort(404, 'repository not registered')

    entry = db[repository]
    chat_id = entry['chat_id']
    secret = bytes(entry['secret'], 'UTF-8')

    signature = headers.get('X-Hub-Signature').split('=')[1]
    mac = hmac.new(secret, msg=request.data, digestmod=sha1)
    if not hmac.compare_digest(mac.hexdigest(), signature):
        logger.warn('bad secret for %s' % repository)
        bot.send_message(chat_id, 'Received event from a repository '
                         'associated with this chat, but with a bad secret.')
        abort(403, 'bad secret')

    responder = GitHubEventResponder(headers.get('X-GitHub-Event'), payload)
    res = responder.push()
    bot.send_message(
        chat_id,
        parse_mode='Markdown',
        disable_web_page_preview=True,
        **res
    )

    return 'ok'


def main():
    try:
        setup_bot()
        app.run(host='0.0.0.0', port=PORT)
        db.close()
    finally:
        handle_cleanup()


if __name__ == '__main__':
    main()
