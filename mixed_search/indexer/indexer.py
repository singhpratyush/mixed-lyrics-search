from threading import Thread
from time import sleep
from psycopg2 import connect
from crawler.db_operations import get_connection

import xapian


class Indexer:
    def __init__(self):
        self.database = xapian.WritableDatabase(
            'db/',
            xapian.DB_CREATE_OR_OPEN
        )

    def add(self, song):
        indexer = xapian.TermGenerator()
        _id = song[0]
        song_name = song[1]
        movie = song[3]
        lyrics = song[6]
        singers = song[7]
        directors = song[8]
        lyricists = song[9]

        singers, directors, lyricists = configure(singers), configure(
            directors), configure(lyricists)

        doc = xapian.Document()
        indexer.set_document(doc)

        indexer.index_text(song_name, 1, 'XS')
        indexer.index_text(movie, 1, 'XM')
        indexer.index_text(lyrics, 1, 'XL')
        indexer.index_text(singers, 1, 'XI')
        indexer.index_text(directors, 1, 'XD')
        indexer.index_text(lyricists, 1, 'XY')

        combined = song_name + ' ' + movie + ' ' + lyrics + ' ' + \
                   singers + ' ' + directors + ' ' + lyricists

        indexer.index_text(combined)

        doc.set_data(str(_id))

        identifier = u'Q' + str(_id)
        doc.add_boolean_term(identifier)
        self.database.replace_document(identifier, doc)

    def add_multiple(self, songs):
        for song in songs:
            self.add(song)


def configure(name):
    return name.replace(
        '\'',
        ''
    ).replace(
        '[',
        ''
    ).replace(
        ']',
        ''
    ).replace(
        ',',
        ' '
    )


def index_latest():
    sql = 'select * from songs where ' \
          'EXTRACT(\'epoch\' from age(last_updated))/60 < 30;'
    conn, cur = get_connection()
    cur.execute(sql)
    result = cur.fetchall()
    print('Indexing {0} new songs.'.format(len(result)))
    conn.close()
    Indexer().add_multiple(result)


def full_index():
    sql = 'select * from songs;'
    conn, cur = get_connection()
    cur.execute(sql)
    result = cur.fetchall()
    print('Indexing {0} songs.'.format(len(result)))
    conn.close()
    Indexer().add_multiple(result)


def run_indexer():
    while True:
        index_latest()
        sleep(30 * 60)


def start_indexer():
    indexer_thread = Thread(target=run_indexer)
    indexer_thread.daemon = True
    indexer_thread.start()
