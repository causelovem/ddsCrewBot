# -*- coding: utf-8 -*-

import sqlite3 as sql
import config as cfg

ct_text = """CREATE TABLE IF NOT EXISTS PARTICIPANT
            (
            chat_id integer,
            participant_id integer,
            participant_first_name text,
            participant_last_name text,
            participant_username text
            );"""

ct_election_text = """CREATE TABLE IF NOT EXISTS ELECTION
            (
            chat_id integer,
            participant_id integer,
            elec_time integer,
            penalty_time integer,
            penalty_B_time integer
            );"""

ct_election_hist_text = """CREATE TABLE IF NOT EXISTS ELECTION_HIST
            (
            chat_id integer,
            participant_id integer,
            elec_time integer,
            penalty_time integer,
            election_date text
            );"""

ct_chatID_text = """CREATE TABLE IF NOT EXISTS CHAT_ID
            (
            chat_id integer
            );"""

ct_metadata_text = """CREATE TABLE IF NOT EXISTS METADATA
            (
            id_rk integer,
            operation integer,
            chat_id integer,
            participant_id integer,
            value integer,
            operation_date_from text,
            operation_date_to text,
            is_success_flg integer
            );"""

ct_meme_text = """CREATE TABLE IF NOT EXISTS MEME
            (
            chat_id integer,
            name text,
            type text,
            value text
            );"""


ins_lj_participant_election_text = """INSERT INTO ELECTION
            SELECT part.chat_id, part.participant_id,
            cast(0 as integer) as elec_time, cast(0 as integer) as penalty_time,
            cast(0 as integer) as penalty_B_time
            FROM
            PARTICIPANT AS part LEFT JOIN ELECTION as elec
            on (part.chat_id = elec.chat_id and
            part.participant_id = elec.participant_id)
            WHERE elec.participant_id is NULL;"""

sel_all_penalty_time_text = """SELECT part.participant_username, elec.penalty_time, part.participant_id
            FROM ELECTION AS elec JOIN PARTICIPANT as part
            on (part.chat_id = ? and part.chat_id = elec.chat_id and
            part.participant_id = elec.participant_id);"""

# судя по документации библиотеки, использовать ? более секурно, чем %*
ins_text = """INSERT INTO PARTICIPANT
            VALUES (?,?,?,?,?);"""

del_text = """DELETE FROM PARTICIPANT WHERE chat_id = ? and participant_id = ?;"""

del_election_text = """DELETE FROM ELECTION WHERE chat_id = ? and participant_id = ?;"""

sel_all_text = """SELECT * FROM PARTICIPANT WHERE chat_id = ?;"""

sel_text = """SELECT * FROM PARTICIPANT WHERE chat_id = ? and participant_id = ?;"""

sel_election_text = """SELECT * FROM ELECTION WHERE chat_id = ? and participant_id = ?;"""

upd_election_elec_text = """UPDATE ELECTION
            SET elec_time = ?
            WHERE chat_id = ? and participant_id = ?;"""

upd_election_penalty_text = """UPDATE ELECTION
            SET penalty_time = ?
            WHERE chat_id = ? and participant_id = ?;"""

upd_election_penalty_B_text = """UPDATE ELECTION
            SET penalty_B_time = penalty_B_time + 1
            WHERE chat_id = ? and participant_id = ?;"""

sel_election_penalty_B_text = """SELECT chat_id, participant_id, elec_time,
            (penalty_time + penalty_B_time) FROM ELECTION
            WHERE elec_time <> 0"""

reset_election_time_text = """UPDATE ELECTION SET elec_time = ?;"""

reset_penalty_B_time_text = """UPDATE ELECTION SET penalty_B_time = ?;"""

# colect_election_hist_text = """INSERT INTO ELECTION_HIST
#             SELECT elc.*, cast(? as text) FROM ELECTION as elc;"""

colect_election_hist_text = """INSERT INTO ELECTION_HIST
            SELECT elec.chat_id, elec.participant_id, elec.elec_time, elec.penalty_time,
            cast(? as text) FROM ELECTION as elc;"""

sel_chatID_text = """SELECT * FROM CHAT_ID WHERE chat_id = ?;"""

ins_chatID_text = """INSERT INTO CHAT_ID
            VALUES (?);"""

del_chatID_text = """DELETE FROM CHAT_ID WHERE chat_id = ?;"""

sel_all_chatID_text = """SELECT * FROM CHAT_ID;"""

ins_operation_meta_text = """INSERT INTO METADATA
            VALUES (?,?,?,?,?,?,?,?)"""

sel_max_id_rk_meta_text = """SELECT max(id_rk) FROM METADATA"""

sel_operation_meta_text = """SELECT * FROM METADATA
            WHERE operation = ? and is_success_flg = ?"""

upd_operation_meta_text = """UPDATE METADATA
            SET is_success_flg = ?
            WHERE id_rk = ?"""

sel_meme_text = """SELECT * FROM MEME WHERE chat_id = ? AND name = ?;"""

ins_meme_text = """INSERT INTO MEME
            VALUES (?,?,?,?);"""

del_meme_text = """DELETE FROM MEME WHERE chat_id = ? AND name = ?;"""


# создать таблицу
@cfg.loglog(command='create_table', type='ct')
def create_table():
    db = sql.connect(cfg.db_name)
    cursor = db.cursor()
    # таблица участников
    cursor.execute(ct_text)
    # таблица для голосования
    cursor.execute(ct_election_text)
    # таблица истории голосований
    cursor.execute(ct_election_hist_text)
    # таблица чатов, подписавшихся на рассылку разных сообщений ботом
    cursor.execute(ct_chatID_text)
    # таблица метаданных операций
    cursor.execute(ct_metadata_text)
    # таблица мемов
    cursor.execute(ct_meme_text)
    db.commit()


# выполнить sql запрос
@cfg.loglog(command='sql_exec', type='db_exec')
def sql_exec(exec_text, params):
    try:
        db = sql.connect(cfg.db_name)
        cursor = db.cursor()
        cursor.execute(exec_text, params)
        db.commit()
        return cursor.fetchall()
    except Exception:
        return 'ERROR!'


# очистка таблицы голосования, ТОЛЬКО ДЛЯ ТЕСТИРОВАНИЯ!!!
# sql_exec(reset_election_time_text, [0])
# sql_exec("""UPDATE ELECTION SET penalty_time = ?;""", [0])
# print(sql_exec("""DELETE FROM ELECTION_HIST""", []))

# print(sql_exec("""DROP TABLE ELECTION_HIST""", []))
# print(sql_exec(colect_election_hist_text, ['2018-09-06']))
# print(sql_exec("""SELECT * FROM ELECTION_HIST""", []))

# sql_exec("""DROP TABLE METADATA""", [])


# вставить данные в таблицу participant and election
@cfg.loglog(command='insert_into_participants', type='db_common')
def insert_into_participants(chat_id, user):
    db = sql.connect(cfg.db_name)
    cursor = db.cursor()

    # не добавляем дубли
    cursor.execute(sel_text, [chat_id, user.id])
    if len(cursor.fetchall()) != 0:
        return -1

    cursor.execute(ins_text, [chat_id, user.id, user.first_name, user.last_name, user.username])
    # обновляем таблицу голосующих за обед
    cursor.execute(ins_lj_participant_election_text)
    db.commit()
    return 1


# удалить данные из таблиц participant and election по конкретному чату-клиенту
@cfg.loglog(command='delete_from_participants', type='db_common')
def delete_from_participants(chat_id, user_id):
    db = sql.connect(cfg.db_name)
    cursor = db.cursor()
    cursor.execute(del_text, [chat_id, user_id])
    # удаляем участника из таблицы голосующих за обед
    cursor.execute(del_election_text, [chat_id, user_id])
    db.commit()


# вставить данные в таблицу participant and election
@cfg.loglog(command='insert_into_chatID', type='sql_chatID')
def insert_into_chatID(chat_id):
    db = sql.connect(cfg.db_name)
    cursor = db.cursor()

    # не добавляем дубли
    cursor.execute(sel_chatID_text, [chat_id])
    if len(cursor.fetchall()) != 0:
        return -1

    cursor.execute(ins_chatID_text, [chat_id])
    db.commit()
    # обновляем список чатов для использования ботом
    cfg.subscribed_chats_transform(sql_exec(sel_all_chatID_text, []))
    return 1


# удалить данные из таблиц participant and election по конкретному чату-клиенту
@cfg.loglog(command='delete_from_chatID', type='sql_chatID')
def delete_from_chatID(chat_id):
    db = sql.connect(cfg.db_name)
    cursor = db.cursor()
    cursor.execute(del_chatID_text, [chat_id])
    db.commit()
    # обновляем список чатов для использования ботом
    cfg.subscribed_chats_transform(sql_exec(sel_all_chatID_text, []))


# создать таблицы, если их нет
create_table()

# обнуляем таблицу голосования
sql_exec(reset_election_time_text, [0])

# обновляем список чатов, чьи сообщения бот может читать
cfg.subscribed_chats_transform(sql_exec(sel_all_chatID_text, []))

# вытаскиваем максимальный id метаданных
max_id_rk = sql_exec(sel_max_id_rk_meta_text, [])
if max_id_rk[0][0] is None:
    max_id_rk = [(0,)]
cfg.max_id_rk = int(max_id_rk[0][0]) + 1


# db = sql.connect(cfg.db_name)
# cursor = db.cursor()
# cursor.execute('''select * from participant;''')
# cursor.execute('''select * from ELECTION;''')
# print(cursor.fetchall())
# db.commit()
