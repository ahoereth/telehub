import json
import hmac
from os import environ
from hashlib import sha1
from flask import Flask, request, abort, redirect
from telegram import Update

from .db import db
from .bot import bot, dispatcher
from .logger import logger
from .events import GitHubEventResponder


routes = Flask(__name__)


@routes.route('/set_webhook', methods=['GET'])
def set_webhook():
    if bot.setWebhook('https://{}/{}'.format(URL, TOKEN)):
        return 'webhook setup ok'
    else:
        abort(400, 'webhook setup failed')


@routes.route('/{}'.format(environ.get('TOKEN')), methods=['POST'])
def telegram():
    """Telegram webhook endpoint.
    """
    dispatcher.process_update(Update.de_json(request.json, bot))
    return 'ok'


@routes.route('/', methods=['POST'])
def github():
    """GitHub webhook endpoint.
    """
    headers = request.headers
    payload = request.json
    repository = payload['repository']['full_name']
    event = headers.get('X-GitHub-Event')
    signature = headers.get('X-Hub-Signature').split('=')[1]
    # deliveryid = headers.get('X-GitHub-Delivery')

    chats = db.get(repository)
    if not chats:
        abort(404, 'repository not registered')

    delivered = 0
    for chat_id, sec in chats.items():
        mac = hmac.new(bytes(sec, 'UTF-8'), msg=request.data, digestmod=sha1)
        if not hmac.compare_digest(mac.hexdigest(), signature):
            logger.warn('bad secret for %s' % repository)
            bot.send_message(chat_id, 'Received event with bad secret.')
            abort(403, 'bad secret')

        res = GitHubEventResponder(event, payload)
        message = res.get_message()
        if message:
            bot.send_message(chat_id, **message)
            delivered += 1

    if delivered:
        return 'telegram message dispatched'
    else:
        return 'no message to dispatched'


@routes.route('/', methods=['GET'])
def landing():
    return redirect('https://github.com/ahoereth/telehub', code=302)
