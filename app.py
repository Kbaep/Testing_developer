import datetime
import os
from time import sleep

import dotenv
import gspread
import psycopg2
from oauth2client.service_account import ServiceAccountCredentials

from services import currency_value_in_rub, send_msg

dotenv.load_dotenv('.env')

try:
    # Подключение к базе данных
    connection = psycopg2.connect(
        host=os.environ.get('HOST'),
        user=os.environ.get('USER'),
        password=os.environ.get('PASSWORD'),
        database=os.environ.get('DB_NAME')
    )

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT version();"
        )

        print(f"Server version: {cursor.fetchone()}")

    # Создание таблицы или подключение
    with connection.cursor() as cursor:
        cursor.execute("""CREATE TABLE IF NOT EXISTS testing(
           id INT,
           order_id INT,
           delivery_time VARCHAR ,
           cost_usa INT,
           cost_rub INT,
           delay TEXT NOT NULL DEFAULT 'Нет',
           delivered TEXT NOT NULL DEFAULT 'Нет'
           );
        """)
        # Сохранение данных БД
        connection.commit()
        print("[INFO] Table connect successfully")

except Exception as _ex:
    print("[INFO] Error while working with PostgreSQL", _ex)


def check_table(data: list):
    """Функция парсит полученные данные из таблицы Google sheets"""
    with connection.cursor() as cursor:
        for row in data:
            # Проверка наличия данных в DB по № строки
            cursor.execute("SELECT * FROM testing WHERE id = %s", (row['№'],))
            db_order = cursor.fetchall()
            if len(db_order) != 0:
                if db_order[0][1] != row['заказ №'] \
                        or db_order[0][2] != row['срок поставки'] or \
                        db_order[0][3] != row['стоимость,$']:
                    cursor.execute(
                        "UPDATE testing SET order_id = %s,"
                        " delivery_time = %s,"
                        " cost_usa = %s,"
                        " cost_rub = %s"
                        " WHERE id = %s",
                        (row['заказ №'],
                         row['срок поставки'],
                         row['стоимость,$'],
                         currency_value_in_rub(row['стоимость,$'],
                                               row['срок поставки']),
                         row['№'],))
                    connection.commit()
            elif len(db_order) == 0:
                cursor.execute("INSERT INTO testing VALUES("
                               "%s, %s, %s, %s, %s ,"
                               "DEFAULT ,DEFAULT );",
                               (row['№'],
                                row['заказ №'],
                                row['срок поставки'],
                                row['стоимость,$'],
                                currency_value_in_rub(row['стоимость,$'],
                                                      row['срок поставки'])))
                connection.commit()


def checking_extra_lines(data: list):
    '''Удаление строк из БД'''
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM testing")
        all_table = cursor.fetchall()
        if len(all_table) > len(data):
            for row in range(len(data), len(all_table)):
                cursor.execute("DELETE FROM testing WHERE id = %s",
                               (all_table[row][0],))
                connection.commit()


def send_telegram():
    '''Отправки уведомлений в telegram'''
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM testing WHERE delay = %sAND"
                       " delivered = %s",
                       ('Нет', 'Нет',))
        all_table = cursor.fetchall()
        for i in all_table:
            if datetime.datetime.strptime(i[2], '%d.%m.%Y') < \
                    datetime.datetime.now():
                pass
                send_msg(f'Прошёл срок по поставке заказа № {i[1]},'
                         f' плановая дата поставки {i[2]}')
                cursor.execute(
                    "UPDATE testing SET delay = %s WHERE id = %s",
                    ('Да', i[0],))
                connection.commit()


if __name__ == '__main__':
    while True:
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        google_sheets_data = ServiceAccountCredentials. \
            from_json_keyfile_name(os.environ.get('API_JSON_GOOGLE'), scope)
        client = gspread.authorize(google_sheets_data)
        sheet = client.open("тестовое").sheet1
        data = sheet.get_all_records()
        check_table(data)
        checking_extra_lines(data)
        send_telegram()
        sleep(600)
