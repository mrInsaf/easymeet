import sqlite3
from sqlite3 import IntegrityError
import datetime


# установите путь к базе данных, если он отличается от директории с программой
connect = sqlite3.connect('C:/Users/stepa/Desktop/Учеба/3 курс/Майнор/easy_meet_db/easy_meet.db')
connect.execute("PRAGMA foreign_keys = 1")
cursor = connect.cursor()

def select(query):
    cursor.execute(query)
    records = cursor.fetchall()
    for rec in records:
        print(rec)
    connect.commit()

def insert(table_name, record):
    cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    table_info = cursor.fetchone()[0]

    # проверяем, есть ли в таблице table_name столбец с первичным ключом
    if "PRIMARY KEY" in table_info:
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [column[1] for column in cursor.fetchall()]
        query = f"""INSERT INTO {table_name} ({str(columns[1:]).replace('[', '').replace(']', '').replace("'", '')}) VALUES ({','.join(['?'] * len(record))});"""
    else:
        query = f"""INSERT INTO {table_name} VALUES ({','.join(['?'] * len(record))});"""

    try:
        cursor.execute(query, record)
        connect.commit()
    except IntegrityError:
        print(f'В родительской таблице нет ключа с таким id для записи:\n {record}\n')

def create_group(date, time, address):
    datetime_str = date + ' ' + time
    record = [address, datetime_str]
    insert('groups', record)

def create_trip(group_id, user_id, departure, transport_type, interim_point=None):
    record = [group_id, user_id, departure, interim_point, transport_type]
    insert('trips', record)

def create_user(chat_id, username, first_name=None, last_name=None):
    record = [chat_id, username, first_name, last_name]
    insert('users', record)
