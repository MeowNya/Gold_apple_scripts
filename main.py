#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'MeowNya'


import datetime as DT
import time
import sys

import requests
from bs4 import BeautifulSoup

import config
import tg_notify_bot


def data_read() -> str:
    return config.LAST_VALUE.read_text('utf-8')


def data_write(last_value: str):
    config.LAST_VALUE.write_text(last_value, 'utf-8')


url = 'https://goldapple.ru/brands/elian-russia'

prev_val = None
if config.LAST_VALUE.exists():
    prev_val = data_read()

while True:
    rs = requests.get(url)

    soup = BeautifulSoup(rs.content, "html.parser")

    need = soup.select_one("#toolbar-amount > .toolbar-number").text
    print(f"{need} товаров {DT.datetime.now():%H:%M %d.%m.%Y}")

    if prev_val is None:
        prev_val = need
        data_write(need)

    if prev_val != need:
        prev_val = need
        data_write(need)

        print(f"Alarm! Warning! Products = {need} now!", file=sys.stderr)
        tg_notify_bot.send_message(config.CHAT_ID, f"Alarm! Warning! Products = {need} now!")

    time.sleep(60*60)
