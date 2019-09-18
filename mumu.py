# -*- coding: utf-8 -*-

import urllib
from lxml import html
import config as cfg


# генерирует url в зависимости от дня недели и номера обеда
# для изображений генерирует тег для поиска, после которого будет url изображения
def generate_url(for_text, week_day, lunch_num, error_url=False):
    # for_text = 'text' - URL for text
    # for_text = 'image' - URL for image
    # week_day - 0mnd-6snd
    # lunch_num - mumu.py has 2 lunches
    # иногда вместо 'ponedelnik-1' URL имеет вид 'ponedelnik-1-'
    # error_url = True - добавлять '-' в конец
    url = ''
    if for_text == 'text' and error_url is True:
        url = 'https://www.cafemumu.ru/catalog/lanchi/lanch-' + \
            cfg.week[week_day] + '-' + str(lunch_num) + '-'
    if for_text == 'text' and error_url is False:
        url = 'https://www.cafemumu.ru/catalog/lanchi/lanch-' + \
            cfg.week[week_day] + '-' + str(lunch_num)
    if for_text == 'image':
        url = '<img alt="Ланч ' + \
            cfg.week_rus[week_day] + ' №' + \
            str(lunch_num) + '" class="imgs" itemprop="image" src="'
    return url


# находим в html по url текст в теге с составом ланча
def find_lunch(url):
    try:
        response = urllib.request.urlopen(url)
        html_text = response.read()
        tree = html.fromstring(html_text)
        lunch = tree.xpath(
            '//*[@id="view-dish"]/div[3]/div/div[3]/span[3]')[0].text
        return lunch
    except urllib.error.HTTPError:
        return 'NOT VALID URL!!!'


# находим в html ссылку на картинку ланча в теге с картинкой
def find_lunch_picture(url):
    try:
        response = urllib.request.urlopen(url)
        html_text = response.read()
        tree = html.fromstring(html_text)
        lunch = tree.xpath('//*[@id="view-dish"]/div[3]/div/div[1]/img[1]')[0]
        return lunch.attrib['src']
    except urllib.error.HTTPError:
        return 'NOT VALID URL!!!'


# определяем день недели и выводим состав ланча и url картинки для обоих ланчей
def lunches(week_day):
    res = []
    for i in range(1, 5):
        lunch_res = []
        # проверяем обычную ссылку
        url = generate_url('text', week_day, i)
        lunch = find_lunch(url)
        # если обычная не работает, проверяем ссылку с '-'
        if lunch == 'NOT VALID URL!!!':
            url = generate_url('text', week_day, i, error_url=True)
            lunch = find_lunch(url)
        # если одна из двух ссылок сработала, записываем результат, находим картинку
        if lunch != 'NOT VALID URL!!!':
            lunch_res.append('Lunch #' + str(i) + ' ' + lunch)
            url_image = generate_url('image', week_day, i)
            image = find_lunch_picture(url)
            lunch_res.append('https://www.cafemumu.ru' + image)
            res.append(lunch_res)
            # print lunch_res
            # print i, url, lunch
    if len(res) == 0:
        res.append(['-', '-'])
        res.append(['-', '-'])
    # вывод ланч-картинка ланч-картинка
    # print res[0][0], res[0][1]
    # print res[1][0], res[1][1]
    return res
