#!/usr/bin/python3.4
import sqlite3
from collections import namedtuple


def rowfactory(cursor, row):
    fields = [col[0] for col in cursor.description]
    Row = namedtuple("Row", fields)
    return Row(*row)


con = sqlite3.connect('agent.db')
con.row_factory = rowfactory

cur = con.cursor()
# cur.execute('''delete from stateaction''')
cur.execute('''create table stateaction
prev_state real, prev_action real, curr_state real,
curr_action real, energy_delta real)''')
cur.execute('''insert into stateaction values (123723245, 1, 7652346234, 2, -1)''')

# cur.execute('''delete from stateaction where prev_state = 0 or curr_state = 0''')
cur.close()
con.commit()
