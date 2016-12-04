#!/usr/bin/env python3
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from os import environ  # nopep8
from flask import Flask  # nopep8
from lib import db, routes  # nopep8


URL = environ.get('URL')
PORT = environ.get('PORT')
TOKEN = environ.get('TOKEN')


def main():
    try:
        routes.run(host='0.0.0.0', port=PORT)
    finally:
        db.close()


if __name__ == '__main__':
    main()
