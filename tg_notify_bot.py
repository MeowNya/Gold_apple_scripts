#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'MeowNya'


from telegram import Bot
from telegram.ext import Updater, Defaults

import config


def send_message(chat_id: int, text: str):
    updater = Updater(
        token=config.TOKEN,
        defaults=Defaults(run_async=True),
    )
    bot: Bot = updater.bot
    bot.send_message(chat_id, text)


if __name__ == '__main__':
    send_message(config.CHAT_ID, "tytuytuxxcvcbvcbnuiyyiu7787878979")
