# -*- coding: utf-8 -*-
import config as cfg
import text_processing as tp
import telebot
import time
import datetime
import database as db
import random
import event_timer as evt
import webhook
import adminId
import retrying
import utils

random.seed(time.clock())

bot = telebot.TeleBot(cfg.token)
cfg.bot = bot

# таймеры
# evt.dinner_time_timer(bot)
evt.one_hour_timer(bot)
evt.check_metadata(bot)


# инициализация в чате
@bot.message_handler(commands=['start'])
@cfg.loglog(command='start', type='message')
@retrying.retry(stop_max_attempt_number=cfg.max_att, wait_random_min=cfg.w_min, wait_random_max=cfg.w_max)
def start_bot(message):
    cid = message.chat.id
    bot.send_message(cid, cfg.hello_msg)

    # инициируем настройки по умолчанию для новых чатов
    db.default_settings(cid)
    utils.upd_din_time(cid)


# приветствие
@bot.message_handler(commands=['help'])
@cfg.loglog(command='help', type='message')
@retrying.retry(stop_max_attempt_number=cfg.max_att, wait_random_min=cfg.w_min, wait_random_max=cfg.w_max)
def send_help(message):
    cid = message.chat.id
    bot.send_message(cid, cfg.hello_msg)


# регистрируем человека в списке участников чата по его запросу
@bot.message_handler(commands=['subscribe'])
@cfg.loglog(command='subscribe', type='message')
@retrying.retry(stop_max_attempt_number=cfg.max_att, wait_random_min=cfg.w_min, wait_random_max=cfg.w_max)
def subscribe(message):
    cid = message.chat.id
    bot.send_chat_action(cid, 'typing')
    user = message.from_user
    res = db.insert_into_participants(cid, user)
    if res == -1:
        bot.send_message(cid, cfg.err_subscribe_msg)
    else:
        bot.send_message(cid, cfg.subscribe_msg)


# удаляем человека из списка участников чата по его запросу
@bot.message_handler(commands=['unsubscribe'])
@cfg.loglog(command='unsubscribe', type='message')
@retrying.retry(stop_max_attempt_number=cfg.max_att, wait_random_min=cfg.w_min, wait_random_max=cfg.w_max)
def unsubscribe(message):
    cid = message.chat.id
    bot.send_chat_action(cid, 'typing')
    user_id = message.from_user.id
    db.delete_from_participants(cid, user_id)
    bot.send_message(cid, cfg.unsubscribe_msg)


# регистрируем чат в рассылки на сообщения ботом
@bot.message_handler(commands=['admin_subscribe_chat'])
@cfg.loglog(command='admin_subscribe_chat', type='message')
@retrying.retry(stop_max_attempt_number=cfg.max_att, wait_random_min=cfg.w_min, wait_random_max=cfg.w_max)
def admin_subscribe_chat(message):
    cid = message.chat.id
    res = db.insert_into_chatID(cid)
    if res == -1:
        bot.send_message(cid, cfg.err_subscribe_msg_chatId)
    else:
        bot.send_message(cid, cfg.subscribe_msg_chatId)


# удаляем чат из рассылки на сообщения ботом
@bot.message_handler(commands=['admin_unsubscribe_chat'])
@cfg.loglog(command='admin_unsubscribe_chat', type='message')
@retrying.retry(stop_max_attempt_number=cfg.max_att, wait_random_min=cfg.w_min, wait_random_max=cfg.w_max)
def admin_unsubscribe_chat(message):
    cid = message.chat.id
    db.delete_from_chatID(cid)
    bot.send_message(cid, cfg.unsubscribe_msg_chatId)


# призвать всех
@bot.message_handler(commands=['all'])
@cfg.loglog(command='all', type='message')
@retrying.retry(stop_max_attempt_number=cfg.max_att, wait_random_min=cfg.w_min, wait_random_max=cfg.w_max)
def ping_all(message):
    cid = message.chat.id
    bot.send_chat_action(cid, 'typing')
    user_id = message.from_user.id
    users = db.sql_exec(db.sel_all_text, [cid])
    call_text = '@all: '
    # бежим по всем юзерам в чате
    for i in users:
        # если юзер не тот, кто вызывал all, уведомляем его
        if i[1] != user_id:
            call_text = call_text + '@' + str(i[0]) + ' '

    bot.send_message(cid, call_text.strip() + message.text[4:])


# подбросить монетку
@bot.message_handler(commands=['coin'])
@cfg.loglog(command='coin', type='message')
@retrying.retry(stop_max_attempt_number=cfg.max_att, wait_random_min=cfg.w_min, wait_random_max=cfg.w_max)
def throw_coin(message):
    cid = message.chat.id
    bot.send_message(cid, random.choice(cfg.precomand_text))
    bot.send_chat_action(cid, 'typing')
    time.sleep(1)

    bot.send_message(cid, random.choice(cfg.coin_var))


# подбросить кубик
@bot.message_handler(commands=['dice'])
@cfg.loglog(command='dice', type='message')
@retrying.retry(stop_max_attempt_number=cfg.max_att, wait_random_min=cfg.w_min, wait_random_max=cfg.w_max)
def throw_dice(message):
    cid = message.chat.id
    bot.send_message(cid, random.choice(cfg.precomand_text))
    bot.send_chat_action(cid, 'typing')
    time.sleep(1)

    if len(message.text.split()) == 2 and message.text.split()[1].isdigit():
        bot.send_message(cid, random.randint(1, int(message.text.split()[1])))
    else:
        bot.send_message(cid, random.choice(cfg.dice_var))


# магический шар
@bot.message_handler(commands=['ball'])
@cfg.loglog(command='ball', type='message')
@retrying.retry(stop_max_attempt_number=cfg.max_att, wait_random_min=cfg.w_min, wait_random_max=cfg.w_max)
def magic_ball(message):
    cid = message.chat.id
    bot.send_message(cid, random.choice(cfg.precomand_ball))
    bot.send_chat_action(cid, 'typing')
    time.sleep(1)

    bot.reply_to(message, random.choice(cfg.ball_var))


# показать время обеда
@bot.message_handler(commands=['dinner'])
@cfg.loglog(command='dinner', type='message')
@retrying.retry(stop_max_attempt_number=cfg.max_att, wait_random_min=cfg.w_min, wait_random_max=cfg.w_max)
def show_dinner_time(message):
    cid = message.chat.id
    bot.send_message(cid, random.choice(cfg.dinner_text) + '<b>' + cfg.show_din_time[cid] + '</b>',
                     parse_mode='HTML')


# сделать SQL запрос
@bot.message_handler(commands=['sqlsql'])
@cfg.loglog(command='sqlsql', type='message')
@retrying.retry(stop_max_attempt_number=cfg.max_att, wait_random_min=cfg.w_min, wait_random_max=cfg.w_max)
def sqlsql(message):
    cid = message.chat.id
    user = message.from_user.id
    bot.send_chat_action(cid, 'typing')

    sqlQuery = message.text[8:]
    print(sqlQuery)

    if sqlQuery.find(';') != -1:
        bot.send_message(cid, 'Запрос надо писать без ";"!')
    else:
        if user == adminId.adminId:
            res = db.sql_exec(sqlQuery, [])
            resStr = '[]'
            if res is None:
                resStr = 'Ошибка в SQL запросе!'
            else:
                for i in res:
                    resStr += str(i) + '\n'
            bot.send_message(cid, str(resStr))
        else:
            bot.send_message(cid, 'Извините, онолитики, я выполняю выполняю только запросы разработчика!')


# показать/оставить штрафы
@bot.message_handler(commands=['penalty'])
@cfg.loglog(command='penalty', type='message')
@retrying.retry(stop_max_attempt_number=cfg.max_att, wait_random_min=cfg.w_min, wait_random_max=cfg.w_max)
def penalty(message):
    time_now = datetime.datetime.now()
    cid = message.chat.id
    bot.send_chat_action(cid, 'typing')
    pen = db.sql_exec(db.sel_all_penalty_time_text, [cid])

    cmd = message.text.split()
    flg = 0

    if (len(cmd) == 3) and (cmd[1].lower() == 'cancel') and (cmd[2].isdigit()):
        # отмена штрафа
        rk = int(cmd[2])
        meta = db.sql_exec(db.sel_meta_by_rk, [rk])

        if len(meta) == 0:
            bot.send_message(cid, 'Штрафа с таким номером не существует!')
        else:
            meta = meta[0]
            dttm = datetime.datetime.strptime(meta[5], '%Y-%m-%d %H:%M:%S')
            val = int(meta[4])
            sign = val / abs(val)

            # 1(active) = 1(positive penalty)
            if (dttm.date() == time_now.date()) and (meta[7] == sign):
                if meta[3] == message.from_user.id:
                    bot.send_message(cid, cfg.self_penalty.format('отменять'))
                else:
                    db.sql_exec(db.upd_operation_meta_text, [3, rk])
                    bot.send_message(cid, cfg.cancel_penalty.format(rk))
            else:
                bot.send_message(cid, 'Данный штраф уже невозможно отменить!')
    elif (len(cmd) == 3) and (not cmd[1].isdigit()) and (cmd[2].isdigit()):
        # постановка штрафа
        for user in pen:
            if user[0] == cmd[1][1:]:
                flg = 1

                if user[2] == message.from_user.id:
                    bot.send_message(cid, cfg.self_penalty.format('ставить'))
                    break

                penalty_time = abs(int(cmd[2]))
                if penalty_time != 0:
                    if penalty_time > utils.getSettings(cid, 'max_deviation').seconds // 60:
                        bot.send_message(cid, 'Я не ставлю штрафы больше чем на максимальное отклонение!')
                    else:
                        # добавляем строку штрафа в метаданные
                        delta = datetime.timedelta(hours=24)
                        expire_date = time_now + delta

                        db.sql_exec(db.ins_operation_meta_text,
                                    [cfg.max_id_rk, 0, cid, user[2], penalty_time,
                                     str(time_now)[:-7], str(expire_date)[:-7], 1])
                        cfg.max_id_rk += 1

                        bot.send_message(cid, cfg.set_penalty.format(str(cmd[1]),
                                                                     str(penalty_time), cfg.max_id_rk - 1))
                else:
                    bot.send_message(cid, 'Я не ставлю штрафы 0 минут!')
                break

        if flg == 0:
            bot.send_message(cid, cfg.no_member.format(str(cmd[1])))
    else:
        # вывод списка штрафов
        pen_msg = 'Штрафы на сегодня:\n'
        pen_msg_flg = 0
        for user in pen:
            if int(user[1]) != 0:
                pen_msg += str(user[0]) + ' — <b>' + str(user[1]) + '</b> мин\n'
                pen_msg_flg = 1

        if pen_msg_flg == 1:
            bot.send_message(cid, pen_msg, parse_mode='HTML')
        else:
            bot.send_message(cid, random.choice(cfg.penalty_empty_text))


# добавить мем
@bot.message_handler(commands=['meme_add'])
@cfg.loglog(command='meme_add', type='message')
@retrying.retry(stop_max_attempt_number=cfg.max_att, wait_random_min=cfg.w_min, wait_random_max=cfg.w_max)
def meme_add(message):
    utils.meme_add_processing(message, 'link', bot)


# удалить мем
@bot.message_handler(commands=['meme_del'])
@cfg.loglog(command='meme_del', type='message')
@retrying.retry(stop_max_attempt_number=cfg.max_att, wait_random_min=cfg.w_min, wait_random_max=cfg.w_max)
def meme_del(message):
    cid = message.chat.id
    bot.send_chat_action(cid, 'typing')

    query = message.text.strip().split()

    if len(query) != 2:
        bot.send_message(cid, cfg.meme_dict_text['del_query_error'])
    else:
        meme_name = query[-1].strip().lower()
        if meme_name.isdigit() is True:
            res = db.sql_exec(db.del_meme_id_text, [cid, meme_name])
        else:
            res = db.sql_exec(db.del_meme_name_text, [cid, meme_name])

        if res is not None:
            bot.send_message(cid, cfg.meme_dict_text['del_success'])
        else:
            bot.send_message(cid, cfg.meme_dict_text['del_unknown_error'])


# мемы
@bot.message_handler(commands=['meme'])
@cfg.loglog(command='meme', type='message')
@retrying.retry(stop_max_attempt_number=cfg.max_att, wait_random_min=cfg.w_min, wait_random_max=cfg.w_max)
def meme(message):
    cid = message.chat.id
    bot.send_chat_action(cid, 'typing')

    query = message.text.strip().split()

    if len(query) == 1:
        res = db.sql_exec(db.sel_meme_in_chat_text, [cid])
        if len(res) == 0:
            bot.send_message(cid, cfg.meme_dict_text['meme_no_memes'])
        else:
            resStr = 'Мемы, добавленные в ваш чат:\n'
            for i in res:
                resStr += '<b>{}. {}</b>\n'.format(str(i[0]), str(i[1]))
            bot.send_message(cid, str(resStr), parse_mode='HTML')
    elif len(query) == 2:
        meme_name = query[-1].strip().lower()
        mem = None
        if meme_name.isdigit() is False:
            mem = db.sql_exec(db.sel_meme_name_text, [cid, meme_name])
        else:
            mem = db.sql_exec(db.sel_meme_id_text, [cid, meme_name])

        if len(mem) == 0:
            bot.send_message(cid, cfg.meme_dict_text['meme_no_mem_in_chat'].format(meme_name))
        else:
            if mem[0][0] == 'photo':
                bot.send_photo(cid, mem[0][1])
            elif mem[0][0] == 'video':
                bot.send_video(cid, mem[0][1])
            elif mem[0][0] == 'link':
                bot.send_message(cid, mem[0][1])
    else:
        bot.send_message(cid, cfg.meme_dict_text['meme_query_error'])


# команда nsfw (скрыть с экрана нежелательный контент)
@bot.message_handler(commands=['nsfw'])
@cfg.loglog(command='nsfw', type='message')
@retrying.retry(stop_max_attempt_number=cfg.max_att, wait_random_min=cfg.w_min, wait_random_max=cfg.w_max)
def nsfw(message):
    utils.nsfw_print(message.chat.id, bot)


# обработка caption у фото и видео
@bot.message_handler(content_types=['photo', 'video'])
@cfg.loglog(command='media_caption', type='media')
@retrying.retry(stop_max_attempt_number=cfg.max_att, wait_random_min=cfg.w_min, wait_random_max=cfg.w_max)
def media_caption(message):
    if message.caption is not None:
        if message.caption.find('/nsfw') != -1:
            utils.nsfw_print(message.chat.id, bot)
        elif message.caption.startswith('/meme_add'):
            utils.meme_add_processing(message, message.content_type, bot)


# settings
@bot.message_handler(commands=['settings'])
@cfg.loglog(command='settings', type='message')
@retrying.retry(stop_max_attempt_number=cfg.max_att, wait_random_min=cfg.w_min, wait_random_max=cfg.w_max)
def settings(message):
    cid = message.chat.id
    bot.send_message(cid, cfg.settings_msg)


# update дефолтного времени обеда
@bot.message_handler(commands=['settings_default_time'])
@cfg.loglog(command='settings_default_time', type='message')
@retrying.retry(stop_max_attempt_number=cfg.max_att, wait_random_min=cfg.w_min, wait_random_max=cfg.w_max)
def settings_default_time(message):
    cid = message.chat.id
    try:
        msg = message.text.lower().strip().split()
        # отображаем текущее значение настройки
        if len(msg) == 1:
            bot.send_message(cid, cfg.curr_value_info + cfg.settings_tovar_dict[msg[0]] + ': <b>' +
                             str(utils.getSettings(cid, 'default_dinner_time'))[:-3] + '</b>.',
                             parse_mode='HTML')
        # проверяем корректность ввода
        elif len(msg) == 2 and tp.time_checker(msg[1]):
            chatSettings = utils.getSettings(cid)
            time = [int(m) for m in msg[1].split(':')]
            newTime = datetime.timedelta(hours=time[0], minutes=time[1])
            # проверяем, что время по умолчанию + время отклонения не превышает сутки
            if (newTime + chatSettings['max_deviation']).days > 0:
                bot.send_message(cid, cfg.err_time_limit, parse_mode='HTML')
            # проверяем, что время по умолчанию меньше, чем конец голосования
            elif chatSettings['elec_end_hour'] >= newTime.seconds // 3600:
                bot.send_message(cid, cfg.big_end_error, parse_mode='HTML')
            elif chatSettings['default_dinner_time'] == newTime:
                bot.send_message(cid, 'Новое время совпадает с текущим.', parse_mode='HTML')
            else:
                # пересчитываем настройку в оперативке
                cfg.settings[cid]['default_dinner_time'] = newTime
                bot.send_message(cid, 'Время обеда по умолчанию изменено, новое значение: <b>' +
                                 msg[1] + '</b>.',
                                 parse_mode='HTML')
                # обновление времени обеда в результате сдвига дефолтного времени
                utils.upd_din_time(cid)
                # уведомление пользователей если время обеда сдвинулось
                bot.send_message(cid, 'С учётом сдвига времени обеда по умолчанию, сегодня обедаем в: <b>' +
                                 cfg.show_din_time[cid] + '</b>.',
                                 parse_mode='HTML')
                # записываем изменения в БД
                db.sql_exec(db.update_time_setting_text, [time[0], time[1], cid])
        else:
            bot.send_message(cid, cfg.err_wrong_cmd.format(msg[0] + ' HH:MM'), parse_mode='HTML')
    except Exception as e:
        print('***ERROR: Проблема с командой settings_default_time***')
        print('Exception text: ' + str(e))


# update среднего времени отклонения от обеда
@bot.message_handler(commands=['settings_max_deviation'])
@cfg.loglog(command='settings_max_deviation', type='message')
@retrying.retry(stop_max_attempt_number=cfg.max_att, wait_random_min=cfg.w_min, wait_random_max=cfg.w_max)
def settings_max_deviation(message):
    cid = message.chat.id
    try:
        msg = message.text.lower().strip().split()
        # отображаем текущее значение настройки
        if len(msg) == 1:
            bot.send_message(cid, cfg.curr_value_info + cfg.settings_tovar_dict[msg[0]] + ': <b>' +
                             str(utils.getSettings(cid, 'max_deviation').seconds // 60) + '</b> минут.',
                             parse_mode='HTML')
        # проверяем корректность ввода
        elif len(msg) == 2 and tp.minute_checker(msg[1]):
            chatSettings = utils.getSettings(cid)
            deviation = datetime.timedelta(minutes=int(msg[1]))
            # проверяем, что время по умолчанию + время отклонения не превышает сутки
            if (deviation + chatSettings['default_dinner_time']).days > 0:
                bot.send_message(cid, cfg.err_time_limit, parse_mode='HTML')
            elif chatSettings['max_deviation'] == deviation:
                bot.send_message(cid, 'Новое отклонение совпадает с текущим.', parse_mode='HTML')
            else:
                # обновляем настройку в оперативке
                cfg.settings[cid]['max_deviation'] = deviation
                bot.send_message(cid, 'Максимальное время отклонения от обеда изменено, новое значение: <b>' +
                                 msg[1] + '</b> минут.',
                                 parse_mode='HTML')
                # обновляем настройку в БД
                db.sql_exec(db.update_deviation_setting_text, [int(msg[1]), cid])
                # TODO: пересчёт votemax
        else:
            bot.send_message(cid, cfg.err_wrong_cmd.format(msg[0] + ' MM'), parse_mode='HTML')
    except Exception as e:
        print('***ERROR: Проблема с командой settings_max_deviation***')
        print('Exception text: ' + str(e))


# update конца голосования за обед
@bot.message_handler(commands=['settings_election_end_hour'])
@cfg.loglog(command='settings_election_end_hour', type='message')
@retrying.retry(stop_max_attempt_number=cfg.max_att, wait_random_min=cfg.w_min, wait_random_max=cfg.w_max)
def settings_election_end_hour(message):
    cid = message.chat.id
    try:
        msg = message.text.lower().strip().split()
        # отображаем текущее значение настройки
        if len(msg) == 1:
            bot.send_message(cid, cfg.curr_value_info + cfg.settings_tovar_dict[msg[0]] + ': <b>' +
                             str(utils.getSettings(cid, 'elec_end_hour')) + '</b>.',
                             parse_mode='HTML')
        # проверяем корректность ввода
        elif len(msg) == 2 and tp.hour_checker(msg[1]):
            chatSettings = utils.getSettings(cid)
            new_elec_end_hour = int(msg[1])
            # проверяем, что время по умолчанию меньше, чем конец голосования
            if new_elec_end_hour >= chatSettings['default_dinner_time'].seconds // 3600:
                bot.send_message(cid, cfg.big_end_error, parse_mode='HTML')
            elif chatSettings['elec_end_hour'] == new_elec_end_hour:
                bot.send_message(cid, 'Новое время окончания голосования совпадает с текущим.',
                                 parse_mode='HTML')
            else:
                # обновляем настройку в оперативке
                cfg.settings[cid]['elec_end_hour'] = new_elec_end_hour
                bot.send_message(cid, 'Время окончания голосования изменено, новое значение: <b>' +
                                 msg[1] + '</b>.', parse_mode='HTML')
                # обновляем настройку в БД
                db.sql_exec(db.update_elec_end_hour_setting_text, [int(msg[1]), cid])
        else:
            bot.send_message(cid, cfg.err_wrong_cmd.format(msg[0] + ' HH'), parse_mode='HTML')
    except Exception as e:
        print('***ERROR: Проблема с командой settings_election_end_hour***')
        print('Exception text: ' + str(e))


# update флаговых настроек
@bot.message_handler(commands=['settings_autodetect_vote', 'settings_lolkek',
                               'settings_voronkov', 'settings_pidor'])
@cfg.loglog(command='settings_flg', type='message')
@retrying.retry(stop_max_attempt_number=cfg.max_att, wait_random_min=cfg.w_min, wait_random_max=cfg.w_max)
def settings_flg(message):
    cid = message.chat.id
    try:
        msg = message.text.lower().strip().split()
        # отображаем текущее значение настройки
        if len(msg) == 1:
            bot.send_message(cid, cfg.curr_value_info + cfg.settings_tovar_dict[msg[0]] + ': ' +
                             cfg.flg_check[utils.getSettings(cid, cfg.settings_tovar_dict[msg[0]])],
                             parse_mode='HTML')
        # проверяем корректность ввода
        elif len(msg) == 2 and msg[1] in cfg.flg_dict:
            if utils.getSettings(cid, cfg.settings_tovar_dict[msg[0]]) == cfg.flg_dict[msg[1]]:
                bot.send_message(cid, 'Новое значение совпадает с текущим.', parse_mode='HTML')
            else:
                # обновляем в оперативке
                cfg.settings[cid][cfg.settings_tovar_dict[msg[0]]] = cfg.flg_dict[msg[1]]
                bot.send_message(cid, 'Настройка ' + msg[0][10:] + cfg.flg_rus[msg[1]], parse_mode='HTML')
                # обновляем в БД
                db.sql_exec(db.update_flg_setting_text.format(cfg.settings_todb_dict[msg[0]],
                                                              cfg.flg_dict[msg[1]], cid), [])
        else:
            bot.send_message(cid, cfg.err_wrong_cmd.format(msg[0] + ' on/off'), parse_mode='HTML')
    except Exception as e:
        print('***ERROR: Проблема с командой settings_flg***')
        print('Exception text: ' + str(e))


# ручное голосование
@bot.message_handler(commands=['vote'])
@cfg.loglog(command='vote', type='message')
@retrying.retry(stop_max_attempt_number=cfg.max_att, wait_random_min=cfg.w_min, wait_random_max=cfg.w_max)
def vote_cmd(message):
    try:
        cid = message.chat.id
        msg = message.text.strip().split()
        # проверка корректности ввода
        if len(msg) == 2 and tp.dinner_election(msg[1], cid, manual=True) is not False:
            week_day = datetime.datetime.today().weekday()
            hour_msg = time.localtime(message.date).tm_hour
            din_elec = int(msg[1])
            # проверяем что сегодня не выходной и время меньше чем час обеда в этом чате
            if week_day not in (5, 6) and hour_msg < utils.getSettings(cid, 'elec_end_hour'):
                bot.send_chat_action(cid, 'typing')
                utils.vote_func(din_elec, bot, message)
            else:
                bot.reply_to(message, cfg.too_late_err)
        else:
            bot.send_message(cid, cfg.err_wrong_cmd.format('vote [+/-]NN'), parse_mode='HTML')
    except Exception as e:
        print('***ERROR: Проблема с командой vote_cmd***')
        print('Exception text: ' + str(e))


# отправка смеющегося стикера
@bot.message_handler(commands=['lol', 'kek'])
@cfg.loglog(command='lol/kek', type='message')
@retrying.retry(stop_max_attempt_number=cfg.max_att, wait_random_min=cfg.w_min, wait_random_max=cfg.w_max)
def lol_kek(message):
    try:
        cid = message.chat.id
        bot.send_sticker(cid, random.choice(cfg.sticker_var))
    except Exception as e:
        print('***ERROR: Проблема с командой lol/kek***')
        print('Exception text: ' + str(e))


# показать номер чата
@bot.message_handler(commands=['show_chat_id'])
@cfg.loglog(command='show_chat_id', type='message')
@retrying.retry(stop_max_attempt_number=cfg.max_att, wait_random_min=cfg.w_min, wait_random_max=cfg.w_max)
def show_chat_id(message):
    try:
        cid = message.chat.id
        bot.send_message(cid, 'Номер вашего чата: <b>{}</b>'.format(cid), parse_mode='HTML')
    except Exception as e:
        print('***ERROR: Проблема с командой show_chat_id***')
        print('Exception text: ' + str(e))


@bot.message_handler(content_types=['text'])
@cfg.loglog(command='text_parser', type='text')
@retrying.retry(stop_max_attempt_number=cfg.max_att, wait_random_min=cfg.w_min, wait_random_max=cfg.w_max)
def text_parser(message):
    week_day = datetime.datetime.today().weekday()
    # нужно брать дату из даты сообщения
    hour_msg = time.localtime(message.date).tm_hour
    cid = message.chat.id

    if cid in cfg.subscribed_chats:
        # лол кек ахахаха детектор
        if utils.getSettings(cid, 'lol_kek') == 1 and tp.lol_kek_detector(message.text) is True:
            if random.random() >= 0.8:
                bot.send_sticker(cid, random.choice(cfg.sticker_var))
                print('Sent!')

        # голосование за обед
        if utils.getSettings(cid, 'autodetect_vote') == 1:
            din_elec = tp.dinner_election(message.text, cid)
            # проверяем что сегодня не выходной и время меньше чем час обеда в этом чате
            if week_day not in (5, 6) and hour_msg < utils.getSettings(cid, 'elec_end_hour') and din_elec:
                bot.send_chat_action(cid, 'typing')
                utils.vote_func(din_elec, bot, message)

print('here')
webhook.webhook(bot)
print('here again')
