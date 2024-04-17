#! /usr/bin/env python3

import argparse
import re
import json
from collections import defaultdict

class mydict(dict):
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value

stats = mydict()

def handleCall(sql_type, table, rows_affected, rows_returned):
    if not 'cnt' in stats[table][sql_type]:
        stats[table][sql_type]['cnt'] = 1
    else:
        stats[table][sql_type]['cnt'] += 1
    if not 'rows_affected' in stats[table][sql_type]:
        stats[table][sql_type]['rows_affected'] = int(rows_affected)
    else:
        stats[table][sql_type]['rows_affected'] += int(rows_affected)
    if not 'rows_returned' in stats[table][sql_type]:
        stats[table][sql_type]['rows_returned'] = int(rows_returned)
    else:
        stats[table][sql_type]['rows_returned'] += int(rows_returned)

    if table != '_TOTAL':
        handleCall(sql_type, '_TOTAL', rows_affected, rows_returned)


def handleInsert(query, rows_affected, rows_returned):
    reInsert = "INSERT\s*INTO\s*(\w+)"
    m = re.search(reInsert, query)
    if not m:
        print(f'Failed Parse: [{query}]')
    else:
        handleCall("INSERT",m.group(1), rows_affected, rows_returned)

def handleUpdate(query, rows_affected, rows_returned):
    reUpdate = "UPDATE\s*(\S+)"
    m = re.search(reUpdate, query)
    if not m:
        print(f'Failed Parse: [{query}]')
    else:
        handleCall("UPDATE",m.group(1), rows_affected, rows_returned)

def handleSelect(query, rows_affected, rows_returned):
    reSelect = "SELECT[\s\S]+FROM\s*(\S+)"
    m = re.search(reSelect, query)
    if not m:
        print(f'Failed Parse: [{query}]')
    else:
        handleCall("SELECT",m.group(1), rows_affected, rows_returned)

def handleDelete(query, rows_affected, rows_returned):
    reDelete = "DELETE\s*FROM\s*(\S+)"
    m = re.search(reDelete, query)
    if not m:
        print(f'Failed Parse: [{query}]')
    else:
        handleCall("DELETE",m.group(1), rows_affected, rows_returned)

parser = argparse.ArgumentParser()
parser.add_argument('file', type=argparse.FileType('r'), nargs='+')
parser.add_argument('-t', '--debugTrace', dest='debugTrace', action='store_true', default=False, help='output debug trace information')
args = parser.parse_args()

reQuery = "QUERY\[([^\]]+)\]\s*BINDVALS\[[^\]]+\]\s*ROWSAFFECTED\[(\d+)\]\s*ROWSRETURNED\[(\d+)\]\s*TIME\[\d+us\]\s*EXCEPTION\[(\S+)\]"
reType = "(\S+)";
for f in args.file:
    for line in f:
        m = re.search(reQuery,line)
        if (m):
            #print(m.groups())
            query = m.group(1).upper()
            rows_affected = int(m.group(2))
            rows_returned = int(m.group(3))
            exception = m.group(4) == "TRUE"
            m = re.search(reType,query)

            match m.group(1):
                case "INSERT":
                    handleInsert(query, rows_affected, rows_returned)
                case "UPDATE":
                    handleUpdate(query, rows_affected, rows_returned)
                case "SELECT":
                    if rows_affected > 0:
                        print(line)
                    handleSelect(query, rows_affected, rows_returned)
                case "DELETE":
                    handleDelete(query, rows_affected, rows_returned)
                case _:
                    print(f'Unknown type [{m.group(1)}] in [{query}]')

print(json.dumps(stats, sort_keys=True))

