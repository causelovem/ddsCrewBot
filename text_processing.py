# -*- coding: utf-8 -*-
import config as cfg
import re


# проверка на мягкий знак в сообщении
def soft_sign(msg):
    res = re.search('ь', msg, flags=re.M | re.I)
    if res is None:
        return False
    else:
        return True


def lol_kek_detector(msg):
    res = re.search(r'\b((л[о|е|у|и|а]+л)|(к[е|и|э]+к)|((ахах)+|(хаха)+)|(ор[у|эйро]*\b)+|(l[o|e|i]+l)|(k[e|i]+k))', msg, flags=re.I)
    if res is None:
        return False
    else:
        return True


# проверяем валидность голоса за обед в автоматическом или ручном захвате
def dinner_election(msg, cid, manual=False):
    if manual:
        res = re.findall('^[+|-]?[0-9]{1,2}$', msg)
    else:
        res = re.findall('^[+|-][0-9]{1,2}$', msg)
    if res == []:
        return False
    else:
        if abs(int(res[0])) <= cfg.settings[cid]['max_deviation'].seconds // 60:
            return int(res[0])
        else:
            return False


# проверяем валидность времени (настройка дефолтного времени обеда)
def time_checker(msg):
    res = re.match(r'^([01]?[0-9]|2[0-3]):([0-5][0-9])$', msg)
    if res is None:
        return False
    else:
        return True


# проверяем валидность минут (настройка макс.отклонения)
def minute_checker(msg):
    res = re.match(r'^([0-9]|([1-9][0-9]))$', msg)
    if res is None:
        return False
    else:
        return True


# проверяем валидность часов
def hour_checker(msg):
    res = re.match(r'^([01]?[0-9]|2[0-3])$', msg)
    if res is None:
        return False
    else:
        return True
