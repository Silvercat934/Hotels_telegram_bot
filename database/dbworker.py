import sqlite3 as sq
from sqlite3 import Cursor, OperationalError
from typing import List, Tuple, Union

from config_data.config import States, db_file


def get_current_state(user_id: int) -> int:
    """
    Функция. Получает текущее состояние бота из БД.
    """

    with sq.connect(db_file) as con:
        cur = con.cursor()
        try:
            values = cur.execute("""SELECT * from users""")
            for i_value in values:
                if i_value[0] == user_id:
                    return i_value[1]
        except OperationalError:
            return States.enter_command_state.value


def set_state(user_id: int, value: int) -> None:
    """
    Функция. Меняет текущее состояние бота в БД.
    """

    with sq.connect(db_file) as con:
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS users(
         id INTEGER, state INTEGER)""")

        info = cur.execute('SELECT * FROM users WHERE id=?', (user_id,))
        if info.fetchone() is None:
            cur.execute("""INSERT INTO users VALUES(?, ?)""", (user_id, value))
        else:
            cur.execute("""UPDATE users SET state=? WHERE id LIKE ?""", (value, user_id))


def add_note(user_id: int, command: str, time: str) -> None:
    """
    Функция. Добавляет новую запись с параметрами запроса в БД.
    """

    with sq.connect(db_file) as con:
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS parameters(
                 id INTEGER,
                 command TEXT,
                 time TEXT,
                 date_from TEXT,
                 date_to TEXT,
                 distance_range TEXT,
                 destination_id INTEGER
                 )""")
        cur.execute('''INSERT INTO parameters VALUES(?, ?, ?, "?", "?", "?", "?")''', (user_id, command, time))


def update_parameter(user_id: int, column: str, value: Union[str, int]) -> None:
    """
    Функция. Обвновляет значение заданного параметра в БД.
    """
    with sq.connect(db_file) as con:
        cur = con.cursor()
        cur.execute('''UPDATE parameters SET %s=%s WHERE id LIKE %s 
        AND time = (SELECT time FROM parameters WHERE id LIKE %s 
        ORDER BY rowid DESC LIMIT 1)''' % (column, value, user_id, user_id))


def get_parameter(user_id: int, column: str) -> Union[str, int]:
    """
    Функция. Получает значение заданного параметра в БД.
    """

    with sq.connect(db_file) as con:
        cur = con.cursor()
        cur.execute('''SELECT %s FROM parameters WHERE id LIKE %s 
        ORDER BY rowid DESC LIMIT 1''' % (column, user_id))
        value = cur.fetchone()[0]
        return value


def update_results(hotels_lst: List[Tuple]) -> None:
    """
    Функция. Обновляет таблицу с результатами поиска отелей в БД.
    """
    with sq.connect(db_file) as con:
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS results(
                 id INTEGER,
                 time TEXT,
                 hotel_id INTEGER,
                 hotel_name TEXT,
                 address TEXT,
                 distance TEXT,
                 cost TEXT,
                 hotel_url TEXT
                 )""")
        cur.executemany('''INSERT INTO results VALUES(?, ?, ?, ?, ?, ?, ?, ?)''', hotels_lst)


def get_results(user_id: int) -> Cursor:
    """
    Функция. Получает результаты поиска отелей из БД.
    """
    with sq.connect(db_file) as con:
        con.row_factory = sq.Row
        cur = con.cursor()
        cur.execute('''SELECT hotel_id, hotel_name, address, distance, cost, hotel_url
         FROM results WHERE id LIKE %s AND time = (SELECT time FROM parameters WHERE id LIKE %s 
        ORDER BY rowid DESC LIMIT 1)''' % (user_id, user_id))
        return cur


def get_history(user_id: int) -> Cursor:
    """
    Функция. Получает историю поиска отелей в БД.
    """
    with sq.connect(db_file) as con:
        con.row_factory = sq.Row
        cur = con.cursor()
        cur.execute('''SELECT parameters.time, parameters.command, hotel_name, address, hotel_url 
        FROM parameters JOIN results ON results.time = parameters.time WHERE parameters.id = %s''' % (user_id, ))
        return cur
