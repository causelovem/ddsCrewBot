# -*- coding: utf-8 -*-
import config as cfg
import text_processing as tp
import mumu
import telebot
import time
import datetime
import database as db
import random
import event_timer as evt
import webhook

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
def send_welcome(message):
    cid = message.chat.id
    bot.send_message(cid, cfg.hello_msg)


# меню в муму
@bot.message_handler(commands=['chto_v_mumu'])
@cfg.loglog(command='chto_v_mumu', type='message')
def send_mumu(message):
    cid = message.chat.id
    week_day = datetime.datetime.today().weekday()
    lunches = mumu.lunches(week_day)

    bot.send_message(cid, lunches[0][0])
    bot.send_message(cid, lunches[0][1])
    bot.send_message(cid, lunches[1][0])
    bot.send_message(cid, lunches[1][1])


# регистрируем человека в списке участников чата по его запросу
@bot.message_handler(commands=['subscribe'])
@cfg.loglog(command='subscribe', type='message')
def subscribe(message):
    cid = message.chat.id
    user = message.from_user
    res = db.insert_into_participants(cid, user)
    if res == -1:
        bot.send_message(cid, cfg.err_subscribe_msg)
    else:
        bot.send_message(cid, cfg.subscribe_msg)


# удаляем человека из списка участников чата по его запросу
@bot.message_handler(commands=['unsubscribe'])
@cfg.loglog(command='unsubscribe', type='message')
def unsubscribe(message):
    cid = message.chat.id
    user_id = message.from_user.id
    db.delete_from_participants(cid, user_id)
    bot.send_message(cid, cfg.unsubscribe_msg)


# регистрируем чат в рассылки на сообщения ботом
@bot.message_handler(commands=['admin_subscribe_for_messages'])
@cfg.loglog(command='admin_subscribe_for_messages', type='message')
def admin_subscribe_for_dinner(message):
    cid = message.chat.id
    res = db.insert_into_chatID(cid)
    if res == -1:
        bot.send_message(cid, cfg.err_subscribe_msg_chatId)
    else:
        bot.send_message(cid, cfg.subscribe_msg_chatId)


# удаляем чат из рассылки на сообщения ботом
@bot.message_handler(commands=['admin_unsubscribe_for_messages'])
@cfg.loglog(command='admin_unsubscribe_for_messages', type='message')
def admin_unsubscribe_for_dinner(message):
    cid = message.chat.id
    db.delete_from_chatID(cid)
    bot.send_message(cid, cfg.unsubscribe_msg_chatId)


# призвать всех
@bot.message_handler(commands=['all'])
@cfg.loglog(command='all', type='message')
def ping_all(message):
    cid = message.chat.id
    user_id = message.from_user.id
    users = db.sql_exec(db.sel_all_text, [cid])
    call_text = 'Эй, @all: '
    # бежим по всем юзерам в чате
    for i in users:
        # если юзер не тот, кто вызывал all, уведомляем его
        if i[1] != user_id:
            call_text = call_text + '@' + str(i[4]) + ' '

    # проверка на /all@ddsCrewBot
    if (message.text[0:15] == '/all@ddsCrewBot'):
        bot.send_message(cid, call_text.strip() + message.text[15:])
    else:
        bot.send_message(cid, call_text.strip() + message.text[4:])


# подбросить монетку
@bot.message_handler(commands=['coin'])
@cfg.loglog(command='coin', type='message')
def throw_coin(message):
    cid = message.chat.id
    bot.send_message(cid, random.choice(cfg.precomand_text))
    time.sleep(1)

    bot.send_message(cid, random.choice(cfg.coin_var))


# подбросить кубик
@bot.message_handler(commands=['dice'])
@cfg.loglog(command='dice', type='message')
def throw_dice(message):
    cid = message.chat.id
    bot.send_message(cid, random.choice(cfg.precomand_text))
    time.sleep(1)

    if len(message.text.split()) == 2 and message.text.split()[1].isdigit():
        bot.send_message(cid, random.randint(1, int(message.text.split()[1])))
    else:
        bot.send_message(cid, random.choice(cfg.dice_var))


# магический шар
@bot.message_handler(commands=['ball'])
@cfg.loglog(command='ball', type='message')
def magic_ball(message):
    cid = message.chat.id
    bot.send_message(cid, random.choice(cfg.precomand_ball))
    time.sleep(1)

    bot.reply_to(message, random.choice(cfg.ball_var))


# показать время обеда
@bot.message_handler(commands=['dinner'])
@cfg.loglog(command='dinner', type='message')
def show_dinner_time(message):
    cid = message.chat.id
    bot.send_message(cid, random.choice(cfg.dinner_text) + cfg.show_din_time)


# показать/оставить штрафы
@bot.message_handler(commands=['penalty'])
@cfg.loglog(command='penalty', type='message')
def penalty(message):
    time_now = datetime.datetime.now()
    cid = message.chat.id
    pen = db.sql_exec(db.sel_all_penalty_time_text, [cid])

    cmd = message.text.split()
    flg = 0

    if (len(cmd) == 3) and (not cmd[1].isdigit()) and (cmd[2].isdigit()):
        for user in pen:
            if user[0] == cmd[1][1:]:
                flg = 1

                if user[2] == message.from_user.id:
                    bot.send_message(cid, 'Нельзя ставить штрафы самому себе!')
                    break

                penalty_time = abs(int(cmd[2]))
                if penalty_time != 0:
                    if penalty_time >= 25:
                        bot.send_message(cid, 'Я не ставлю штрафы больше чем на 25 минут!')
                    else:
                        bot.send_message(cid, 'Поставил штраф ' + str(cmd[1]) + ' ' +
                                         str(penalty_time) + ' мин')

                        # добавляем строку штрафа в метаданные
                        delta = datetime.timedelta(hours=24)
                        expire_date = time_now + delta

                        db.sql_exec(db.ins_operation_meta_text,
                                    [cfg.max_id_rk, 0, cid, user[2], penalty_time,
                                     str(time_now)[:-7], str(expire_date)[:-7], 1])
                        cfg.max_id_rk += 1
                else:
                    bot.send_message(cid, 'Я не ставлю штрафы 0 минут!')
                break

        if flg == 0:
            bot.send_message(cid, 'Я не нашёл ' + str(cmd[1]) + ' в базе...\n' +
                             'Проверь написание ника!\n' +
                             'Ну, или может быть этот этот человек ещё не подписался?')
    else:
        pen_msg = 'Штрафы на сегодня:\n'
        pen_msg_flg = 0
        for user in pen:
            if int(user[1]) != 0:
                pen_msg += str(user[0]) + ' — ' + str(user[1]) + ' мин\n'
                pen_msg_flg = 1

        if pen_msg_flg == 1:
            bot.send_message(cid, pen_msg)
        else:
            bot.send_message(cid, random.choice(cfg.penalty_empty_text))


# раскомментировать, чтобы узнать file_id стикера
# @bot.message_handler(content_types=["sticker"])
# def get_sticker(message):
#     print(message.sticker.file_id)
#     cid = message.chat.id
#     bot.send_sticker(cid, random.choice(cfg.sticker_var))


@bot.message_handler(content_types=["text"])
@cfg.loglog(command='text_parser', type='message')
def text_parser(message):
    week_day = datetime.datetime.today().weekday()
    # нужно брать дату из даты сообщения
    hour_msg = time.localtime(message.date).tm_hour
    # текущее время, может пригодиться
    # hour_now = time.localtime().tm_hour
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
        # ТОЛЬКО ДЛЯ ТЕСТИРОВАНИЯ!!!
        # if din_elec is not False:
        if week_day not in (5, 6) and hour_msg < 12 and din_elec is not False:
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
                    sign = (din_elec / abs(din_elec))
                    final_elec_time = din_elec - sign * penalty_time

                if abs(final_elec_time) > 25:
                    final_elec_time = sign * 25

                if (sign * final_elec_time < 0):
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
                        sign = (prev_din_elec / abs(prev_din_elec))
                        final_elec_time = prev_din_elec - sign * penalty_time

                    if abs(final_elec_time) > 25:
                        final_elec_time = sign * 25

                    if (sign * final_elec_time < 0):
                        final_elec_time = 0

                    final_elec_time = datetime.timedelta(minutes=final_elec_time)
                    cfg.dinner_time -= final_elec_time
                    bot.reply_to(message, cfg.revote_msg + additional_msg + str(cfg.dinner_time)[:-3])

                cfg.show_din_time = str(cfg.dinner_time)[:-3]
                print('Время обеда', cfg.show_din_time)
                db.sql_exec(db.upd_election_elec_text, [din_elec, cid, user_id])

        # # понеделбник - денб без мягкого знака
        if week_day == 0 and hour_msg < 12 and tp.soft_sign(message.text) is True:
            print('##########', datetime.datetime.now(), 'soft_sign')

            bot.reply_to(message, 'ШТРАФ')
            print('ШТРАФ')

        print('##########', datetime.datetime.now(), '\n')


print('here')
webhook.webhook(bot)
print('here again')
