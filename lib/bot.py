from os import environ
from telegram import Bot
from telegram.ext import Dispatcher, CommandHandler

from .handlers import error, start, subscribe, showhelp


bot = Bot(environ.get('TOKEN'))
dispatcher = Dispatcher(bot, update_queue=None, workers=0)
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', showhelp))
dispatcher.add_handler(CommandHandler('subscribe', subscribe,
                                      pass_args=True, pass_chat_data=True))
dispatcher.add_error_handler(error)
