#!/usr/bin/python3.4
import importlib
import pip


def install_and_import(package):
    try:
        importlib.import_module(package)
    except ImportError:
        pip.main(['install', package])
    finally:
        globals()[package] = importlib.import_module(package)


print("installing required python modules...")

install_and_import('sqlite3')
install_and_import('queue')
install_and_import('tkinter')

# install_and_import('numpy')
# install_and_import('pandas')

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
cur.execute('''create table stateaction2 (prev_state real, prev_action real, curr_state real, curr_action real, energy_delta real)''')
cur.execute('''insert into stateaction values (123723245, 0, 7652346234, 1, 10)''')
cur.execute('''insert into stateaction values (123723245, 1, 7652346234, 2, 10)''')
cur.execute('''insert into stateaction values (123723245, 2, 7652346234, 4, 10)''')
cur.execute('''insert into stateaction values (123723245, 4, 7652346234, 8, 10)''')
cur.execute('''insert into stateaction values (123723245, 8, 7652346234, 0, 10)''')

# cur.execute('''delete from stateaction where prev_state = 0 or curr_state = 0''')
cur.close()
con.commit()

print("Installation complete!")
