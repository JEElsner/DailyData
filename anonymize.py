import sqlite3
import json
import random


def get_activities(con: sqlite3.Connection):
    fetch = con.execute('SELECT name FROM activity').fetchall()

    with open('./anonymize.json', mode='w') as json_file:
        json.dump({row[0]: "" for row in fetch}, json_file)


def scramble_activities(con: sqlite3.Connection):
    acts = ['petting_doge', 'global_thermonuclear_warfare', 'commiting_mild_treason',
            'eating_one_peanut', 'dancing_the_night_away', 'sleeping', 'writing_buggy_code', 'speedwalking']

    con.execute('DELETE FROM activity')
    con.executemany(
        'INSERT INTO activity (name) VALUES (:act)', ((i,) for i in acts))

    ids = map(lambda row: row[0], con.execute(
        'SELECT id FROM timelog').fetchall())

    for id in ids:
        con.execute('UPDATE timelog SET activity=:new_act WHERE id=:id', {
            'new_act': random.choice(acts),
            'id': id
        })


if __name__ == '__main__':
    with sqlite3.connect('./tests/sample.db') as con:
        scramble_activities(con)

        con.commit()
