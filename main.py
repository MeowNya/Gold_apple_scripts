#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'MeowNya'


import datetime as DT
import time
import traceback
import sys

import requests
import re

import config
import tg_notify_bot


def data_read() -> str:
    return config.LAST_VALUE.read_text('utf-8')


def data_write(last_value: str):
    config.LAST_VALUE.write_text(last_value, 'utf-8')


def parse_page():
    session = requests.session()

    url = 'https://goldapple.ru/brands/elian-russia'

    rs = session.get(url)
    m = re.search(r'"productsApiUrl":\s*"(.+?)",', rs.text)
    if not m:
        raise Exception('Не найдена ссылка на API!')

    url_api_products = m.group(1)

    print(f'Using API: {url_api_products}')

    total = 0
    page = 1
    while True:
        rs = session.get(url_api_products, params={'page': page})
        rs.raise_for_status()

        products = rs.json().get('products')
        if not products:
            break

        total += len(products)

        page += 1

    return total


MAX_ATT = 5
err_count = MAX_ATT
prev_val = None
if config.LAST_VALUE.exists():
    prev_val = data_read()
    print(prev_val)

while True:
    try:
        need = str(parse_page())
        print(f"{need} товаров {DT.datetime.now():%H:%M %d.%m.%Y}")

        if prev_val is None:
            prev_val = need
            data_write(need)

        if prev_val != need:
            prev_val = need
            data_write(need)

            print(f"Alarm! Warning! Products = {need} now!", file=sys.stderr)
            tg_notify_bot.send_message(config.CHAT_ID, f"Alarm! Warning! Products = {need} now!")

    except Exception as e:
        print(traceback.format_exc())

        err_count -= 1
        if err_count <= 0:
            tg_notify_bot.send_message(config.CHAT_ID, f"Alarm! Too many retries failed! {e}")
            time.sleep(60*60)

        time.sleep(15)
        continue


    err_count = MAX_ATT
    time.sleep(60*60)
