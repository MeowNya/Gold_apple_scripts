#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'MeowNya'


import datetime as DT
import time
import sys
import logging
from pathlib import Path

import requests
import re

import config
import tg_notify_bot


def get_logger(file_name: str, dir_name='logs'):
    dir_name = Path(dir_name).resolve()
    dir_name.mkdir(parents=True, exist_ok=True)

    file_name = str(dir_name / Path(file_name).resolve().name) + '.log'

    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)

    formatter = logging.Formatter('[%(asctime)s] %(filename)s[LINE:%(lineno)d] %(levelname)-8s %(message)s')

    fh = logging.FileHandler(file_name, encoding='utf-8')
    fh.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(stream=sys.stdout)
    ch.setLevel(logging.DEBUG)

    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    log.addHandler(fh)
    log.addHandler(ch)

    return log


log = get_logger('loggs')


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

    log.debug(f'Using API: {url_api_products}')

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
    log.debug(f"pre_val = {prev_val}")

while True:
    try:
        need = str(parse_page())
        log.debug(f"{need} товаров")

        if prev_val is None:
            prev_val = need
            data_write(need)

        if prev_val != need:
            prev_val = need
            data_write(need)

            log.debug(f"Alarm! Warning! Products = {need} now!")
            tg_notify_bot.send_message(config.CHAT_ID, f"Alarm! Warning! Products = {need} now!")

    except Exception as e:
        log.exception("error: ")

        err_count -= 1
        if err_count <= 0:
            tg_notify_bot.send_message(config.CHAT_ID, f"😡 Alarm! Too many retries failed! 😡 {e}")
            time.sleep(60*60)

        time.sleep(15)
        continue

    err_count = MAX_ATT
    time.sleep(60*60)
