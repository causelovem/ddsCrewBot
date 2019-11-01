# -*- coding: utf-8 -*-
import config as cfg
import text_processing as tp
# import mumu
import telebot
import time
import datetime
import database as db
import random
import event_timer as evt
import webhook
import adminId
import retrying

random.seed(time.clock())

bot = telebot.TeleBot(cfg.token)

# week_day = datetime.datetime.today().weekday()

# определяем дефолтное время
cfg.dinner_time = cfg.dinner_default_time
cfg.dinner_time = datetime.timedelta(hours=cfg.dinner_time[0], minutes=cfg.dinner_time[1])
cfg.show_din_time = str(cfg.dinner_time)[:-3]

# таймеры
# evt.dinner_time_timer(bot)
evt.one_hour_timer(bot)
evt.check_metadata(bot)


# приветствие
@bot.message_handler(commands=['start', 'help'])
@cfg.loglog(command='start/help', type='message')
@retrying.retry(stop_max_attempt_number=cfg.max_att, wait_random_min=cfg.w_min, wait_random_max=cfg.w_max)
def send_welcome(message):
    cid = message.chat.id
    bot.send_message(cid, cfg.hello_msg)


# # меню в муму
# @bot.message_handler(commands=['chto_v_mumu'])
# @cfg.loglog(command='chto_v_mumu', type='message')
# @retrying.retry(stop_max_attempt_number=cfg.max_att, wait_random_min=cfg.w_min, wait_random_max=cfg.w_max)
# def send_mumu(message):
#     cid = message.chat.id
#     bot.send_chat_action(cid, 'typing')
#     week_day = datetime.datetime.today().weekday()
#     lunches = mumu.lunches(week_day)

#     bot.send_message(cid, lunches[0][0])
#     bot.send_message(cid, lunches[0][1])
#     bot.send_message(cid, lunches[1][0])
#     bot.send_message(cid, lunches[1][1])


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
    call_text = 'Эй, @all: '
    # бежим по всем юзерам в чате
    for i in users:
        # если юзер не тот, кто вызывал all, уведомляем его
        if i[1] != user_id:
            call_text = call_text + '@' + str(i[0]) + ' '

    # проверка на /all@ddsCrewBot
    if (message.text[0:15] == '/all@ddsCrewBot'):
        bot.send_message(cid, call_text.strip() + message.text[15:])
    else:
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
    bot.send_message(cid, random.choice(cfg.dinner_text) + '*' + cfg.show_din_time + '*',
                     parse_mode='Markdown')


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
            if res == 'ERROR!':
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
                    if penalty_time > 25:
                        bot.send_message(cid, 'Я не ставлю штрафы больше чем на 25 минут!')
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
                pen_msg += str(user[0]) + ' — *' + str(user[1]) + '* мин\n'
                pen_msg_flg = 1

        if pen_msg_flg == 1:
            bot.send_message(cid, pen_msg, parse_mode='Markdown')
        else:
            bot.send_message(cid, random.choice(cfg.penalty_empty_text))


# функция добавления мема
def meme_add_processing(message, meme_type):
    # /meme_add /https... meme_name | /meme_add meme_name
    cid = message.chat.id
    bot.send_chat_action(cid, 'typing')

    query = None
    if meme_type in ('photo', 'video'):
        query = message.caption.strip().split()
    else:
        query = message.text.strip().split()

    meme_name = query[-1].strip().lower()

    mem = db.sql_exec(db.sel_meme_name_text, [cid, meme_name])

    if len(mem) != 0:
        bot.send_message(cid, cfg.meme_dict_text['add_exist_error'].format(meme_name))
        return

    curr_max_meme_id = db.sql_exec(db.sel_max_meme_id_text, [cid])
    if curr_max_meme_id == []:
        curr_max_meme_id = 1
    else:
        curr_max_meme_id = int(curr_max_meme_id[0][0]) + 1

    if meme_name.isdigit() is True:
        bot.send_message(cid, cfg.meme_dict_text['add_digital_name_error'])
        return

    res = None
    if meme_type == 'photo':
        if len(query) == 2:
            res = db.sql_exec(db.ins_meme_text, [curr_max_meme_id, cid, meme_name, meme_type,
                                                 message.json['photo'][-1]['file_id']])
        else:
            bot.send_message(cid, cfg.meme_dict_text['add_media_query_error'])
            return
    elif meme_type == 'video':
        if len(query) == 2:
            res = db.sql_exec(db.ins_meme_text, [curr_max_meme_id, cid, meme_name, meme_type,
                                                 message.json['video']['file_id']])
        else:
            bot.send_message(cid, cfg.meme_dict_text['add_media_query_error'])
            return
    elif meme_type == 'link':
        if len(query) == 3:
            res = db.sql_exec(db.ins_meme_text, [curr_max_meme_id, cid, meme_name, 'link',
                                                 query[1].strip()])
        else:
            bot.send_message(cid, cfg.meme_dict_text['add_link_query_error'])
            return

    if res != 'ERROR!':
        bot.send_message(cid, cfg.meme_dict_text['add_success'].format(meme_name))
    else:
        bot.send_message(cid, cfg.meme_dict_text['add_unknown_error'])


# добавить мем
@bot.message_handler(commands=['meme_add'])
@cfg.loglog(command='meme_add', type='message')
@retrying.retry(stop_max_attempt_number=cfg.max_att, wait_random_min=cfg.w_min, wait_random_max=cfg.w_max)
def meme_add(message):
    meme_add_processing(message, 'link')


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

        if res != 'ERROR!':
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

                resStr += '*{}. {}*\n'.format(str(i[0]), str(i[1]))
            bot.send_message(cid, str(resStr), parse_mode='Markdown')
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


# раскомментировать, чтобы узнать file_id фотографии
# @bot.message_handler(content_types=["photo"])
# def get_photo(message):
#     # print(message)
#     # print(str(message.json['photo']))
#     print(message.json['photo'][2]['file_id'])
#     cid = message.chat.id


# раскомментировать, чтобы узнать file_id стикера
# @bot.message_handler(content_types=["sticker"])
# def get_sticker(message):
#     print(message.sticker.file_id)
#     cid = message.chat.id
#     bot.send_sticker(cid, random.choice(cfg.sticker_var))


# функция вывода nsfw
def nsfw_print(cid):
    bot.send_sticker(cid, cfg.sticker_dog_left)
    bot.send_message(cid, '!!! NOT SAFE FOR WORK !!!\n' * 3)
    bot.send_sticker(cid, random.choice(cfg.sticker_nsfw))
    bot.send_message(cid, '!!! NOT SAFE FOR WORK !!!\n' * 3)
    bot.send_sticker(cid, cfg.sticker_dog_right)


# команда nsfw (скрыть с экрана нежелательный контент)
@bot.message_handler(commands=['nsfw'])
@cfg.loglog(command='nsfw', type='message')
@retrying.retry(stop_max_attempt_number=cfg.max_att, wait_random_min=cfg.w_min, wait_random_max=cfg.w_max)
def nsfw(message):
    nsfw_print(message.chat.id)


# обработка caption у фото и видео
@bot.message_handler(content_types=['photo', 'video'])
@cfg.loglog(command='media_caption', type='message')
@retrying.retry(stop_max_attempt_number=cfg.max_att, wait_random_min=cfg.w_min, wait_random_max=cfg.w_max)
def media_caption(message):
    if message.caption is not None:
        if message.caption.find('/nsfw') != -1:
            nsfw_print(message.chat.id)
        elif message.caption.startswith('/meme_add'):
            meme_add_processing(message, message.content_type)


@bot.message_handler(content_types=["text"])
@cfg.loglog(command='text_parser', type='message')
@retrying.retry(stop_max_attempt_number=cfg.max_att, wait_random_min=cfg.w_min, wait_random_max=cfg.w_max)
def text_parser(message):
    week_day = datetime.datetime.today().weekday()
    # нужно брать дату из даты сообщения
    hour_msg = time.localtime(message.date).tm_hour
    cid = message.chat.id
    user_id = message.from_user.id

    if cid in cfg.subscribed_chats:
        # # лол кек ахахаха детектор
        if tp.lol_kek_detector(message.text) is True:
            print('##########', datetime.datetime.now(), 'lol_kek_detector')

            if random.random() >= 0.8:
                bot.send_sticker(cid, random.choice(cfg.sticker_var))
                print('Sent!')

        # # голосование за обед
        din_elec = tp.dinner_election(message.text)
        if week_day not in (5, 6) and hour_msg < 12 and din_elec is not False:
            bot.send_chat_action(cid, 'typing')
            print('##########', datetime.datetime.now(), 'dinner_election')

            print('Din_elec =', din_elec)
            user = db.sql_exec(db.sel_election_text, [cid, user_id])
            if len(user) == 0:
                bot.reply_to(message, cfg.err_vote_msg)
            else:
                penalty_time = int(user[0][3])

                final_elec_time = 0
                sign = 1

                if din_elec != 0:
                    sign = din_elec / abs(din_elec)
                    final_elec_time = din_elec - sign * penalty_time

                if abs(final_elec_time) > 25:
                    final_elec_time = sign * 25

                if sign * final_elec_time < 0:
                    final_elec_time = 0

                final_elec_time = datetime.timedelta(minutes=final_elec_time)
                cfg.dinner_time += final_elec_time

                additional_msg = ''
                if penalty_time != 0:
                    additional_msg = 'с учётом штрафов '

                # голосование или переголосование
                if int(user[0][2]) == 0:
                    bot.reply_to(message, cfg.vote_msg + additional_msg + str(cfg.dinner_time)[:-3])
                else:
                    final_elec_time = 0
                    prev_din_elec = int(user[0][2])
                    sign = 1

                    if prev_din_elec != 0:
                        sign = prev_din_elec / abs(prev_din_elec)
                        final_elec_time = prev_din_elec - sign * penalty_time

                    if abs(final_elec_time) > 25:
                        final_elec_time = sign * 25

                    if sign * final_elec_time < 0:
                        final_elec_time = 0

                    final_elec_time = datetime.timedelta(minutes=final_elec_time)
                    cfg.dinner_time -= final_elec_time
                    bot.reply_to(message, cfg.revote_msg + additional_msg + str(cfg.dinner_time)[:-3])

                cfg.show_din_time = str(cfg.dinner_time)[:-3]
                print('Время обеда', cfg.show_din_time)
                db.sql_exec(db.upd_election_elec_text, [din_elec, cid, user_id])

        # # понеделбник - денб без мягкого знака
        # if week_day == 0 and hour_msg < 12 and tp.soft_sign(message.text) is True:
        #     print('##########', datetime.datetime.now(), 'soft_sign')

        #     bot.reply_to(message, 'ШТРАФ')
        #     db.sql_exec(db.upd_election_penalty_B_text, [cid, user_id])
        #     print('ШТРАФ')

        print('##########', datetime.datetime.now(), '\n')


print('here')
webhook.webhook(bot)
print('here again')
