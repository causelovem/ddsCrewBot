# -*- coding: utf-8 -*-
import config as cfg
# import text_processing as tp
# import time
import datetime
import database as db
import random


# вернуть время обеда в datetime
def calc_show_din_time(cid):
    return cfg.settings[cid]['default_dinner_time'] + datetime.timedelta(minutes=dinner_vote_sum.get(cid, 0))


# обновить глобальную переменную с временем обеда
def upd_din_time(cid=False):
    # указываем на использование глобальной переменной, иначе не работает
    global dinner_vote_sum
    if cid is False:
        # очищаем время голосов за обед в конце дня
        for chat in cfg.show_din_time.keys():
            dinner_vote_sum[chat] = 0
            cfg.show_din_time[chat] = str(cfg.settings[chat]['default_dinner_time'])[:-3]
    else:
        # пересчитываем время обеда в глобальной переменной
        cfg.show_din_time[cid] = str(calc_show_din_time(cid))[:-3]


# обработка голоса за обед
def vote_func(vote_chat, bot, message):
    cid = message.chat.id
    user_id = message.from_user.id
    dinner_vote = db.sql_exec(db.sel_election_text, [cid, user_id])
    if len(dinner_vote) == 0:
        bot.reply_to(message, cfg.err_vote_msg)
    else:
        vote_db = dinner_vote[0][2]
        penalty_time = dinner_vote[0][3]
        final_elec_time = 0
        sign = 1

        if vote_chat != 0:
            sign = vote_chat / abs(vote_chat)
            final_elec_time = vote_chat - sign * penalty_time

        if abs(final_elec_time) > cfg.settings[cid]['max_deviation'].seconds // 60:
            final_elec_time = sign * cfg.settings[cid]['max_deviation'].seconds // 60

        if sign * final_elec_time < 0:
            final_elec_time = 0

        # final_elec_time = datetime.timedelta(minutes=final_elec_time)
        # считаем сумму голосов отдельно от времени
        dinner_vote_sum[cid] = dinner_vote_sum.get(cid, 0) + final_elec_time

        additional_msg = ''
        if penalty_time != 0:
            additional_msg = 'с учётом штрафов '

        # голосование или переголосование
        if int(vote_db) == 0:
            # обновляем итоговое время обеда
            upd_din_time(cid)
            bot.reply_to(message, cfg.vote_msg + additional_msg + cfg.show_din_time[cid])
        else:
            final_elec_time = 0
            prev_vote_db = int(vote_db)
            sign = 1

            if prev_vote_db != 0:
                sign = prev_vote_db / abs(prev_vote_db)
                final_elec_time = prev_vote_db - sign * penalty_time

            if abs(final_elec_time) > cfg.settings[cid]['max_deviation'].seconds // 60:
                final_elec_time = sign * cfg.settings[cid]['max_deviation'].seconds // 60

            if sign * final_elec_time < 0:
                final_elec_time = 0

            # final_elec_time = datetime.timedelta(minutes=final_elec_time)
            # считаем сумму голосов отдельно от времени обеда
            dinner_vote_sum[cid] -= final_elec_time
            # обновляем итоговое время обеда
            upd_din_time(cid)
            bot.reply_to(message, cfg.revote_msg + additional_msg + cfg.show_din_time[cid])

        print('Время обеда', cfg.show_din_time[cid])
        db.sql_exec(db.upd_election_elec_text, [vote_chat, cid, user_id])


# пересчитать время обеда в оперативке после перезагрузки бота
# @cfg.loglog(command='vote_recalc', type='bot')
# def vote_recalc():
#     dinner_vote = db.sql_exec(db.sel_all_election_text, [])
#     for i in range(len(dinner_vote)):
#         cid = dinner_vote[i][0]
#         # user_id = dinner_vote[i][1]
#         vote_chat = dinner_vote[i][2]
#         penalty_time = dinner_vote[i][3]
#         final_elec_time = 0
#         sign = 1

#         if vote_chat != 0:
#             sign = vote_chat / abs(vote_chat)
#             final_elec_time = vote_chat - sign * penalty_time

#         if abs(final_elec_time) > 25:
#             final_elec_time = sign * 25

#         if sign * final_elec_time < 0:
#             final_elec_time = 0

#         # final_elec_time = datetime.timedelta(minutes=final_elec_time)
#         # считаем сумму голосов отдельно от времени обеда
#         dinner_vote_sum[cid] = dinner_vote_sum.get(cid, 0) + final_elec_time
#         # обновляем итоговое время обеда
#         upd_din_time(cid)


# nsfw print function
def nsfw_print(cid, bot):
    bot.send_sticker(cid, cfg.sticker_dog_left)
    bot.send_message(cid, '!!! NOT SAFE FOR WORK !!!\n' * 3)
    bot.send_sticker(cid, random.choice(cfg.sticker_nsfw))
    bot.send_message(cid, '!!! NOT SAFE FOR WORK !!!\n' * 3)
    bot.send_sticker(cid, cfg.sticker_dog_right)


# функция добавления мема
def meme_add_processing(message, meme_type, bot):
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


dinner_vote_sum = {}
# пересчитываем сумму голосов в оперативке в случае перезагрузки бота в течение дня
# vote_recalc()
