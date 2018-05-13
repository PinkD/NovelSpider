import sqlite3

from novel import Novel


class DatabaseHelper:
    def __init__(self, name='test'):
        self._conn = sqlite3.connect(name + '.db', check_same_thread=False)
        self._init_db()

    def _init_db(self):
        cursor = self._conn.cursor()
        # cursor.execute('DROP TABLE IF EXISTS `novel`')
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS `novel`(
              `id`          INTEGER PRIMARY KEY,
              `title`       TEXT  NOT NULL,
              `author`      TEXT,
              `count`       INTEGER UNSIGNED,
              `description` TEXT,
              `type`        TEXT
            )
            '''
        )
        cursor.close()
        self._conn.commit()

    def insert_novel(self, novel: Novel):
        cursor = self._conn.cursor()
        cursor.execute(
            '''
            INSERT INTO `novel` (id, title, author, count, description, type) VALUES (?, ?, ?, ?, ?, ?)
            '''
            , (novel.id, novel.title, novel.author, novel.count, novel.description, novel.type)
        )
        cursor.close()
        self._conn.commit()

    def check_novel_exists(self, id):
        cursor = self._conn.cursor()
        cursor.execute(
            '''
            SELECT id FROM `novel` WHERE `id` = ?
            '''
            , (id,)
        )
        result = cursor.fetchall()
        cursor.close()
        return result
