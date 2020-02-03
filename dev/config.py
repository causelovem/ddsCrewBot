# -*- coding: utf-8 -*-

# токен бота вынесен в отдельный файл,
# чтобы не выкладывать его в открытый доступ
import tokenBot
import datetime

# токен бота
token = tokenBot.token

# название бота
bot_name = 'ddsCrewBot'

# приветственное сообщение бота
hello_msg = '''Привет! Я бот для чата DDS. Если тебе это ничего не говорит, иди своей дорогой дальше.
Я уже умею достаточно много чего, но всё равно буду расти:
/all MESSAGE(optional)- пингануть всех в чате
/coin - подбросить монетку
/dice - подбросить кубик
/ball - магический шар
/vote N - проголосовать за время обеда
/dinner - показать время обеда
/penalty - показать текущие штрафы
/penalty @Username N - поставить штраф
/penalty cancel N - отменить штраф
/meme NAME/ID - показать мем NAME/ID
/meme_add LINK NAME - добавить мем-ссылку в чат
/meme_add NAME - добавить мем-фото/видео в чат (ввести в подпись к фото/видео)
/meme_del NAME/ID - удалить мем из чата
/nsfw - поднимает потенциально непристойное сообщение наверх, чтобы его не было видно
/subscribe - подписаться на рассылку @all
/unsubscribe - отписаться от рассылки @all
/admin_subscribe_chat - подписать чат на чтение сообщений ботом и рассылки уведомлений
/admin_unsubscribe_chat - отписать чат от чтения сообщений ботом и рассылки уведомлений
/settings - настройки бота
'''

settings_msg = '''Доступные настройки:
/settings_default_time HH:MM - время обеда по умолчанию
/settings_max_deviation MM - максимальное отклонение от времени обеда в минутах
/settings_autodetect_vote on/off - управление автоматическим чтением голосов в чате
/settings_lolkek on/off - управление реакцией бота на лол кек в чате
/settings_voronkov on/off - управление напоминаниями от Воронкова
'''
# TODO: /settings_pidor on/off - управление встроенным пидором

# название базы данных пользователей в чатах
db_name = 'bot_database.db'

# сообщение о подписке на бота человеком
subscribe_msg = '''Принято! Ты подписан на рассылку /all
и теперь можешь голосовать за время обеда.
ВНИМАНИЕ! Бот собирает статистику голосования, если тебе это не нравится,
то ты можешь отписаться командой /unsubscribe в любое время.'''

# сообщение об отписке от бота человеком
unsubscribe_msg = '''Принято! Ты отписан от рассылки /all
и теперь не можешь голосовать за время обеда.'''

# сообщение о повторной подписке человеком
err_subscribe_msg = '''Ты уже подписан! Ты можешь отписаться командой /unsubscribe в любое время.'''

# сообщение о подписке на бота чатом
subscribe_msg_chatId = '''Принято! Бот читает ваши сообщения :)
Теперь в вашем чате можно голосовать за время обеда и получать различные напоминания.'''

# сообщение об отписке от бота чатом
unsubscribe_msg_chatId = '''Принято! Бот больше не читает ваши сообщения :(
Теперь в вашем чате нельзя голосовать за время обеда и получать различные напоминания.'''

# сообщение о повторной подписке чатом
err_subscribe_msg_chatId = '''Ваш чат уже подписан!
Вы можете отписаться командой /admin_unsubscribe_chat в любое время.'''

# сообщение при голосовании
vote_msg = '''Ты проголосовал!\nТекущее время '''

# сообщение при переголосовании
revote_msg = '''Ты переголосовал!\nТекущее время '''

# сообщение об ошибке при голосовании
err_vote_msg = '''Ты не можешь голосовать за время обеда :(
Для этого ты должен подписаться на /all
Ты можешь сделать это командой /subscribe'''

# ошибка установки/отмены штрафа себе
self_penalty = '''Нельзя {} штрафы самому себе!'''

# установка штрафа
set_penalty = '''Поставил штраф {} {} мин
Номер штрафа {}'''

# отмена штрафа
cancel_penalty = '''Отменил штраф с номером {}'''

# не существует пользователя
no_member = '''Я не нашёл {} в базе...
Проверь написание ника!
Ну, или может быть этот человек ещё не подписался?'''

# ошибки команд
err_wrong_cmd = '''Ошибка: Неправильное использование команды, формат ввода: '''
err_time_limit = '''Ошибка: Максимально возможное время обеда превышает одни сутки.
Измените время обеда по умолчанию или среднее время отклонения.'''
too_late_err = '''Слишком поздно для голосования за время обеда!'''

# информация о текущем значении настройки
curr_value_info = '''Текущее значение настройки '''

# дефолтное время обеда (часы, минуты)
dinner_default_time = (12, 45)
# дефолтное время отклонения от обеда
dinner_default_plusminus_time = 25
# dinner_time = 0

# дефолтные флаги
autodetect_vote_default = 1
lol_kek_default = 1
voronkov_default = 0
pidor_default = 0

# настройки во всех чатах
settings = {}

# список чатов, чьи сообщения бот читает
subscribed_chats = []

# максимальный id в метаданных
max_id_rk = 0

# флаг ошибки метаданных
meta_error_flg = 0

# максимальное количество попыток перезапуска команды
max_att = 3
# минимальное время ожидания между попытками
w_min = 200
# максимальное время ожидания между попытками
w_max = 700

# стикер кот-ебан file_id
stiker_kot_eban = 'CAADBAADcAAD-OAEAsKXeIPkd1o3Ag'

# список стикеров
sticker_var = ['CAADBAADcAAD-OAEAsKXeIPkd1o3Ag', 'CAADAgADAgADwXKkBLMxNUOXvJrUAg',
               'CAADAgADAQADwXKkBKKoPDv9KrHpAg', 'CAADAgADBwADwXKkBDaH1tzzKIZdAg',
               'CAADAgADAwADwXKkBDjiVNM0pYEPAg']

# стикер бегущая собака (налево) (nsfw начало)
sticker_dog_left = 'CAADAgADSgADCvzCBT4D4LGJM21JFgQ'

# стикер бегущая собака (направо) (nsfw конец)
sticker_dog_right = 'CAADAgADXwADCvzCBagU3QxA1vSQFgQ'

# список стикеров для nsfw (середина)
sticker_nsfw = ['CAADAgADDwIAAnELQgUswU-6Q5RnnRYE', 'CAADAgADFwADPR6-DdUKOy0QNzy9FgQ']

# прекомандный текст
precomand_text = ['Легко!', 'Пожалуйста!', 'Запросто!', 'Ложись!', 'Лови!', 'Конечно!']

# пекоманды для шара
precomand_ball = ['Трясу шар...', 'Секунду...', 'Сейчас посмотрим...', 'Ща...']

# варианты монетки
coin_var = ['Орёл', 'Решка']

# варианты кубика
dice_var = ['1', '2', '3', '4', '5', '6']

# варианты магического шара
ball_var = ['Бесспорно', 'Предрешено', 'Никаких сомнений', 'Определённо да',
            'Можешь быть уверен в этом', 'Мне кажется — да', 'Вероятнее всего',
            'Хорошие перспективы', 'Знаки говорят — да', 'Да', 'Пока не ясно, попробуй снова',
            'Спроси позже', 'Лучше не рассказывать', 'Сейчас нельзя предсказать',
            'Сконцентрируйся и спроси опять', 'Даже не думай', 'Мой ответ — нет',
            'По моим данным — нет', 'Перспективы не очень хорошие', 'Весьма сомнительно'
            ]

# переменная для показа времени
show_din_time = {}

# текст "доброе утро"
gm_text = ['С добрым утром, работяги!', 'Мир, труд, май!', 'Ммм... Работка!', 'Нада роботац!']

# текст "уходить с работы"
bb_text = ['Пора домой!', 'Работать хорошо, но дома лучше!', 'Пора валить!',
           'Хватит сидеть! Иди домой.']

# текст напоминай о голосовании
vote_notif_text = ['Ты давай-ка голосуй, а не то получишь...', 'Надо бы за обед проголосовать...',
                   'Там обед скоро, держу в курсе.', 'Значёчек с циферкой напиши в чат, пожалуйста.']

# текст, когда все проголосовали
success_vote_notif_text = ['Даже напоминать про голосование некому!', 'Все проголосовали, какие молодцы!']

# текст напоминания об скором выходе на обед
dinner_notif_text = ['Коллеги, скоро обед!\n', 'Доделываем дела, скоро выходим на обед!\n']

# текст "попить"
pitb_text = ['Может попить? /pitb', 'Просто так напомню, что можно сходить попить... /pitb',
             'Го пить? /pitb']

# текст "дсс"
dss_text = ['Завтра DSS, держу в курсе!', 'Иди приготовь поесть, завтра DSS.']

# текст "поесть"
eat_text = ['Вроде как 17:00... Может поесть?', 'Что на счёт поесть?']

# текст "обед"
dinner_text = ['Сегодняшнее время обеда ', 'Сегодня выходим в ', 'Сегодня пойдём есть в ']

# сообщение об отсутствие штрафов
penalty_empty_text = ['Сегодня штрафов ни у кого нет!',
                      'Сегодня штрафы по нулям. Какие же мы все молодцы!',
                      'На сегодня без штрафов, но впредь, будьте аккуратнее!']

# текст воронкова
voronkov_text = [[', привет', 'скажи, пжл', 'какой текущий статус по ', '?'],
                 [', привет', 'уточни статус', ' по ', ')'],
                 [', привет', 'когда отправишь БФТЗ', ' по ', '?'],
                 [', привет', 'скажи, пжл', 'какой текущий статус разработки по ', '?']]

stiker_voronkov = 'CAADAgADBwADwXKkBDaH1tzzKIZdAg'

# словарь сообщений для семейства команд "meme"
meme_dict_text = {
    'del_query_error': 'Для удаления мне нужно только название!',
    'del_success': 'Если такой мем и был в вашем чате, то он удалён!',
    'del_unknown_error': 'Какая-то ошибка при удалении мема... Пусть разработчик посмотрит в логи!',
    'add_exist_error': 'Мем "{}" в вашем чате уже существует!',
    'add_link_query_error': 'Какая-то ошибка при добавлении мема.\nНужно указать только ссылку и название мема.',
    'add_media_query_error': 'Какая-то ошибка при добавлении мема.\nПри добавлении мема-фото/видео нужно указать только название мема.',
    'add_success': 'Добавил мем "{0}" в ваш чат!\nВы можете показать мем с помощью команды\n/meme {0}',
    'add_unknown_error': 'Какая-то ошибка при добавлении мема... Пусть разработчик посмотрит в логи!',
    'add_digital_name_error': 'Имя мема не может состоять только из цифр.',
    'meme_no_memes': 'В вашем чате нет мемов :(\nВы можете добавить их командой /meme_add!',
    'meme_no_mem_in_chat': 'Мем "{}" не существует в вашем чате!',
    'meme_query_error': 'Мне нужно только название мема или его номер!'
}

# словарь операций для метаданных
operations = {
    0: 'shtraf',
    1: 'voronkov'
}

# словарь success флага метаданных
is_success_flg = {
    0: 'success',
    1: 'active',
    2: 'error',
    3: 'cancel'
}

# словарь соответствий номера дня недели и английского/русского названия (для генерации ссылок)
week = {
    0: 'ponedelnik',
    1: 'vtornik',
    2: 'sreda',
    3: 'chetverg',
    4: 'pyatnitsa',
    5: 'subbota',
    6: '-'
}


week_rus = {
    0: 'понедельник',
    1: 'вторник',
    2: 'среда',
    3: 'четверг',
    4: 'пятница',
    5: 'суббота',
    6: '-'
}


# словарь флаговых настроек
settings_todb_dict = {
    '/settings_autodetect_vote': 'autodetect_vote_flg',
    '/settings_lolkek': 'lol_kek_flg',
    '/settings_voronkov': 'voronkov_flg',
    '/settings_pidor': 'pidor_flg'
}

settings_tovar_dict = {
    '/settings_default_time': 'default_dinner_time',
    '/settings_max_deviation': 'max_deviation',
    '/settings_autodetect_vote': 'autodetect_vote',
    '/settings_lolkek': 'lol_kek',
    '/settings_voronkov': 'voronkov',
    '/settings_pidor': 'pidor'
}

# словарь переключения настроек
flg_dict = {'on': 1, 'off': 0}
flg_rus = {'on': ' <b>активирована</b>!', 'off': ' <b>деактивирована</b>!'}
flg_check = {1: '<b>активирована</b>.', 0: '<b>деактивирована</b>.'}


# функция для повторения команды бота при выкидывании исключения
def retry_bot_command(command, *args):
    try:
        command(*args)
    except Exception as e:
        print(e)
        print('Попробую ещё раз')
        command(*args)


# функция преобразования списка подписавшихся чатов,
# для более удобного использования
def subscribed_chats_transform(update):
    subscribed_chats.clear()
    for i in update:
        subscribed_chats.append(i[0])


# логирование команд
def loglog(**command):
    def decorator(func):
        def wrapped(*msg):
            if command['type'] == 'message':
                cmdLine = msg[0].text.lower().strip().split()
                cmdName = cmdLine[0].split('@')
                if len(cmdName) == 2 and cmdName[1] == bot_name.lower():
                    cmdLine[0] = cmdName[0]
                    msg[0].text = ' '.join(cmdLine)
                elif len(cmdName) != 1:
                    return

            print('##########', datetime.datetime.now(), command['command'])
            if command['type'] == 'message':
                print('Chat_id =', msg[0].chat.id)
                print('User =', msg[0].from_user.id)
            elif command['type'] in ('db_exec', 'db_common'):
                print('Exec text =', msg[0])
                print('Params =', msg[1])
            elif command['type'] == 'sql_chatID':
                print('Chat_id =', msg[0])

            res = func(*msg)
            print('##########', datetime.datetime.now(), command['command'], '\n')
            return res
        return wrapped
    return decorator
