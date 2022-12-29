import sqlite3

from config.consts import DB_NAME



conn = sqlite3.connect(f'{DB_NAME}.sqlite3')
cur = conn.cursor()