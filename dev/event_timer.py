# -*- coding: utf-8 -*-

import threading as th
import datetime
import config as cfg
import database as db
import random as rnd
import time

rnd.seed(datetime.datetime.now().time().second)


@cfg.loglog(command='call_all', type='bot')
def call_all(query=db.sel_all_text, chat_id=None):
    chatUsers = {}
    if chat_id is None:
        for cid in cfg.subscribed_chats:
            users = db.sql_exec(query, [cid])
            if users == []:
                chatUsers[cid] = ''
                continue
            call_users = 'Эй, @all: '
            for i in users:
                call_users += '@' + str(i[0]) + ' '
            chatUsers[cid] = call_users.strip() + '\n'
    else:
        users = db.sql_exec(query, [chat_id])
        if users == [] or chat_id not in cfg.subscribed_chats:
            chatUsers[chat_id] = ''
            return chatUsers

        call_users = 'Эй, @all: '
        for i in users:
            call_users += '@' + str(i[0]) + ' '
        chatUsers[chat_id] = call_users.strip() + '\n'

    return chatUsers


@cfg.loglog(command='send_msg', type='bot')
def send_msg(bot, msg, cid=None):
    if cid is None:
        for chat_id in cfg.subscribed_chats:
            bot.send_message(chat_id, msg, parse_mode='Markdown')
    else:
        bot.send_message(cid, msg, parse_mode='Markdown')


@cfg.loglog(command='check_metadata', type='bot')
def check_metadata(bot):
    time_now = datetime.datetime.now()
    # выбираем все активные строки из метаданных
    meta = db.sql_exec("""SELECT * FROM METADATA
            WHERE operation in (0, 1) and is_success_flg = ?""", [1])

    # meta = db.sql_exec(db.sel_operation_meta_text, [0, 1])
    # meta.extend(db.sql_exec(db.sel_operation_meta_text, [1, 1]))
    # meta = db.sql_exec(db.sel_operation_meta_text, [(0, 1), 1])

    for m in meta:
        # print(m)

        # '%Y-%m-%d %H:%M:%S'
        dttm = datetime.datetime.strptime(m[6], '%Y-%m-%d %H:%M:%S')

        if (dttm.date() == time_now.date()) and (dttm.time() >= time_now.time()):
            # штрафы
            if m[1] == 0:
                print(m)
                user = db.sql_exec(db.sel_election_text, [m[2], m[3]])
                if len(user) == 0:
                    # обновляем строку в метаданных как ошибочную
                    db.sql_exec(db.upd_operation_meta_text, [2, m[0]])
                    print('!!! ОШИБКА, НЕТ ЮЗЕРА В БАЗЕ ДЛЯ ' + str(m[2]) + ' ' + str(m[3]) + ' !!!')
                else:
                    if m[4] >= 0:
                        # вычисляем дату исполнения
                        # hh = 72
                        # if dttm.weekday() in (3, 4):
                        #     hh = 120
                        # elif dttm.weekday() == 5:
                        #     hh = 96
                        hh = 48
                        if dttm.weekday() in (4, 5):
                            hh = 96
                        if dttm.weekday() == 6:
                            hh = 72

                        delta = datetime.timedelta(hours=hh, minutes=5)
                        # delta = datetime.timedelta(seconds=10)
                        expire_date = time_now + delta

                        db.sql_exec(db.ins_operation_meta_text,
                                    [cfg.max_id_rk, 0, m[2], m[3], - int(m[4]),
                                     str(time_now)[:-7], str(expire_date)[:-7], 1])
                        cfg.max_id_rk += 1

                    penalty = int(user[0][3]) + int(m[4])

                    if penalty < 0:
                        penalty = 0
                    elif penalty > 25:
                        penalty = 25

                    # ставим/убираем штраф
                    db.sql_exec(db.upd_election_penalty_text, [penalty, m[2], m[3]])
                    # обновляем строку в метаданных как успешно отработавшую
                    db.sql_exec(db.upd_operation_meta_text, [0, m[0]])

                print(db.sql_exec("""SELECT * FROM METADATA""", []))
                print(db.sql_exec("""SELECT * FROM ELECTION""", []))
            # воронков
            elif m[1] == 1:
                dttmt = dttm.time()
                expire_time = datetime.timedelta(hours=dttmt.hour, minutes=dttmt.minute,
                                                 seconds=dttmt.second)

                dttmt_now = time_now.time()
                time_now_delta = datetime.timedelta(hours=dttmt_now.hour, minutes=dttmt_now.minute,
                                                    seconds=dttmt_now.second)
                delta = expire_time - time_now_delta

                delta = int(delta.total_seconds()) + 1

                th.Timer(delta, voronkov_timer, args=(bot, m,)).start()
        elif dttm < time_now:
            # обновляем строку в метаданных как ошибочную (не выполнилась в нужную дату или время)
            db.sql_exec(db.upd_operation_meta_text, [2, m[0]])
            print('!!! ОШИБОЧНАЯ СТРОКА В ТАБЛИЦЕ МЕТАДАННЫХ !!!')
            print(m)

            # команду штрафа надо применить в любом случае
            if m[1] == 0:
                cfg.meta_error_flg = 1

                delta = datetime.timedelta(minutes=10)
                expire_date = time_now + delta

                db.sql_exec(db.ins_operation_meta_text,
                            [cfg.max_id_rk, 0, m[2], m[3], m[4],
                             str(time_now)[:-7], str(expire_date)[:-7], 1])
                cfg.max_id_rk += 1


@cfg.loglog(command='voronkov_timer', type='bot')
def voronkov_timer(bot, meta):
    # print(meta)

    user = db.sql_exec(db.sel_text, [meta[2], meta[3]])
    # print(user)
    if user == []:
        users = db.sql_exec(db.sel_all_text, [meta[2]])
        if users != []:
            # user = rnd.choice(users)
            user = [rnd.choice(users)]
            print('! НЕТ ТЕКУЩЕГО ЮЗЕРА, БЫЛ ВЫБРАН ДРУГОЙ !')
        else:
            # обновляем строку в метаданных как ошибочную
            db.sql_exec(db.upd_operation_meta_text, [2, meta[0]])
            print('!!! ОШИБКА, НЕТ ЮЗЕРОВ В БАЗЕ ДЛЯ CHAT_ID = ' + str(meta[2]) + ' !!!')
            return

    # user = '@' + user[0][4]
    user = '@' + user[0][0]

    scenario = rnd.choice(cfg.voronkov_text)
    print(scenario)

    send_msg(bot, user + scenario[0], meta[2])
    time.sleep(1)
    send_msg(bot, scenario[1], meta[2])
    time.sleep(1)
    send_msg(bot, scenario[2] + str(rnd.randint(10000, 19999)), meta[2])
    time.sleep(1)
    send_msg(bot, scenario[3], meta[2])
    bot.send_sticker(meta[2], cfg.stiker_voronkov)

    # обновляем строку в метаданных как успешно отработавшую
    db.sql_exec(db.upd_operation_meta_text, [0, meta[0]])
    # print(db.sql_exec("""SELECT * FROM METADATA""", []))


@cfg.loglog(command='dinner_timer', type='bot')
def dinner_timer(bot, chat_id):
    chatUsers = call_all(db.sel_all_text, chat_id)
    for cid, msg in chatUsers.items():
        if msg == '':
            print('Чат отписался от рассылки, сообщение не отправлено; CHAT_ID = ' + str(cid))
        else:
            send_msg(bot, '{}{}{}*{}*'.format(msg, rnd.choice(cfg.dinner_notif_text), rnd.choice(cfg.dinner_text), cfg.show_din_time), cid)


@cfg.loglog(command='one_hour_timer', type='bot')
def one_hour_timer(bot):
    time_now = datetime.datetime.now()

    # флаг, который говорит, показывать ли сообщения (показывает, когда 1)
    to_show = 0

    # начальное время таймера (60 * 60)
    timer_time = 3600

    # начальная дельта (0)
    delta = datetime.timedelta(seconds=0)

    if str(time_now.time().minute) in ('0'):
        to_show = 1
        if str(time_now.time().second) <= '30':
            # нормальная работа
            timer = th.Timer(timer_time, one_hour_timer, args=(bot,))
        else:
            # случай для возможного увеличения времени из-за расчётов программы
            timer_time -= 29
            timer = th.Timer(timer_time, one_hour_timer, args=(bot,))
    else:
        # рандомное время, например, при запуске бота
        # высчитываем время до ближайшего часа **:00:01
        common_time = datetime.timedelta(minutes=60, seconds=0)
        cur_time = datetime.timedelta(minutes=time_now.time().minute, seconds=time_now.time().second)

        delta = common_time - cur_time

        timer_time = int(delta.total_seconds()) + 1

        timer = th.Timer(timer_time, one_hour_timer, args=(bot,))

    print('Секунды до таймера =', timer_time)
    print('Время до таймера =', delta)

    timer.start()

    if to_show == 1:
        # будние дни
        if time_now.weekday() not in (5, 6):
            # доброе утро и вызвать pidora
            if str(time_now.time().hour) == '9':
                send_msg(bot, rnd.choice(cfg.gm_text))
                send_msg(bot, '/pidor@SublimeBot')

            # напоминание о голосовании за обед
            if str(time_now.time().hour) == '11':
                chatUsers = call_all(db.sel_nonvoted_users_text)
                for cid, msg in chatUsers.items():
                    if msg == '':
                        send_msg(bot, rnd.choice(cfg.success_vote_notif_text), cid)
                    else:
                        send_msg(bot, msg + rnd.choice(cfg.vote_notif_text), cid)

            # обед
            if str(time_now.time().hour) == '12':
                chatUsers = call_all()
                cur_time = datetime.timedelta(hours=time_now.time().hour, minutes=time_now.time().minute, seconds=time_now.time().second)
                for cid, msg in chatUsers.items():
                    if time_now.weekday() == 0:
                        cfg.dinner_time = cfg.dinner_default_time
                        cfg.dinner_time = datetime.timedelta(hours=cfg.dinner_time[0],
                                                             minutes=cfg.dinner_time[1])
                        cfg.show_din_time = str(cfg.dinner_time)[:-3]

                        elec = db.sql_exec(db.sel_election_penalty_B_text, [])

                        final_elec_time = 0
                        for part in elec:
                            elec_time = int(part[2])
                            pen_time = int(part[3])

                            sign = elec_time / abs(elec_time)
                            tmp_time = elec_time - sign * pen_time

                            if abs(tmp_time) > 25:
                                tmp_time = sign * 25

                            if sign * tmp_time < 0:
                                tmp_time = 0

                            final_elec_time += tmp_time

                        final_elec_time = datetime.timedelta(minutes=final_elec_time)
                        cfg.dinner_time += final_elec_time
                        cfg.show_din_time = str(cfg.dinner_time)[:-3]

                    if msg == '':
                        # send_msg(bot, rnd.choice(cfg.dinner_text) + '*' + cfg.show_din_time + '*', cid)
                        send_msg(bot, '{}*{}*'.format(rnd.choice(cfg.dinner_text), cfg.show_din_time), cid)
                    else:
                        # send_msg(bot, msg + rnd.choice(cfg.dinner_text) + '*' + cfg.show_din_time + '*', cid)
                        send_msg(bot, '{}{}*{}*'.format(msg, rnd.choice(cfg.dinner_text), cfg.show_din_time), cid)
                    # сохраняем историю голосования
                    db.sql_exec(db.colect_election_hist_text, [str(time_now.date())])
                    # обнуляем время голосования
                    db.sql_exec(db.reset_election_time_text, [0])
                    # обнуляем время штрафЬ
                    db.sql_exec(db.reset_penalty_B_time_text, [0])

                    # ставим таймер за 10 минут до обеда, о напоминании об обеде
                    delta = cfg.dinner_time - cur_time - datetime.timedelta(minutes=10, seconds=0)
                    th.Timer(int(delta.total_seconds()) + 1, dinner_timer, args=(bot, cid,)).start()

            # # намёк поесть
            # if str(time_now.time().hour) == '17':
            #     send_msg(bot, rnd.choice(cfg.eat_text))

            # пора уходить с работы
            if str(time_now.time().hour) == '19':
                send_msg(bot, rnd.choice(cfg.bb_text))

            # в определённое время намекать на попить
            if str(time_now.time().hour) in ('11', '15', '17', '18'):
                send_msg(bot, rnd.choice(cfg.pitb_text))
        # выходные
        elif time_now.weekday() == 6:
            # напоминать про дсс
            if str(time_now.time().hour) == '19':
                chatUsers = call_all()
                for cid, msg in chatUsers.items():
                    if msg == '':
                        send_msg(bot, rnd.choice(cfg.dss_text), cid)
                    else:
                        send_msg(bot, msg + rnd.choice(cfg.dss_text), cid)

            # поставить таймер на воронкова
            if str(time_now.time().hour) == '23':
                # оставляем небольшой запас времени на вычисления
                # 1 минута и 10 секунд
                hh = rnd.randint(1, 119)
                mm = rnd.randint(1, 58)
                ss = rnd.randint(0, 50)

                # вычисляем дату исполнения
                delta = datetime.timedelta(hours=hh, minutes=mm, seconds=ss)
                expire_date = time_now + delta

                for cid in cfg.subscribed_chats:
                    users = db.sql_exec(db.sel_all_text, [cid])
                    if users != []:
                        call_user = rnd.choice(users)[1]

                        # добавляем строку воронкова в метаданные для каждого чата
                        db.sql_exec(db.ins_operation_meta_text,
                                    [cfg.max_id_rk, 1, cid, call_user, -1,
                                     str(time_now)[:-7], str(expire_date)[:-7], 1])
                        cfg.max_id_rk += 1
                    else:
                        print('! ОШИБКА, НЕТ ЮЗЕРОВ В БАЗЕ ДЛЯ CHAT_ID = ' + str(cid) + ' !')

    # выводим дату для лога и выполняем системные сбросы и таймеры
    if str(time_now.time().hour) == '0':
        print('New day!', time_now)

        # проверяем метаданные и выставляем таймеры
        check_metadata(bot)

        # если произошла ошибка с выставлением штрафа,
        # нужно проверить метаданные ещё раз
        if cfg.meta_error_flg == 1:
            cfg.meta_error_flg = 0
            check_metadata(bot)

        # обнуляем время голосовния в боте
        cfg.dinner_time = cfg.dinner_default_time
        cfg.dinner_time = datetime.timedelta(hours=cfg.dinner_time[0], minutes=cfg.dinner_time[1])
        cfg.show_din_time = str(cfg.dinner_time)[:-3]
