# Скрипт по обработке таблиц Google Sheets, через Google API.

# Подготовка:

В проекте используется Python v3.8

1) В файле `requirements.txt`, указан список использующихся библиотек. Его можно установить по команде в
   терминале: `pip install -r requirements.txt`.


2) Для подключения к базе данных, необходимо создать файл `.env`, и скопировать названия переменных из
   файла `.env_example`, в них внести данные.

   Чтобы получить ключ для работы с API, вы можете, ознакомится со статьёй: 
   [ссылке](https://habr.com/ru/post/483302/)


3) Необходимо установить на компьютере Docker, и запустить базу данных PostgreSQL, по команде в
   терминале: `docker compose up -d db`.


4) Запуск продуктивной файла, можно по команде в терминале: `python app.py`

После запуска в терминале, скрипт подключится к базе данных и начнёт обработку таблицы.

Ссылка на таблицу Google
Sheets: [ссылке](https://docs.google.com/spreadsheets/d/1WX2VJod1-5HfWgPFROMsfbX8builkR35bkG9-xBGrHQ/edit#gid=149663643)
