import csv
import econsult.econsult_data
import sqlite3
import sys
from tqdm import tqdm

def progress(s):
    sys.stdout.write(s)
    sys.stdout.flush()

def main(args):
    if len(args) < 1:
        sys.stderr.write('1 required arguments: <sqlite filename>\n')
        sys.exit(-1)

    in_conn = sqlite3.connect(args[0])
    cur = in_conn.cursor()


    cur.execute('''DROP TABLE IF EXISTS cui_counts''')
    cur.execute('''CREATE TABLE cui_counts (cui text, count int, date text)''')


    cur.execute('select cui from (select cui,count(cui) as frequency from cuis group by cui order by -count(cui) limit 100)')
    cuis = []
    for row in cur:
        cuis.append(row[0])
    
    for year in range(2010, 2017+1):
        progress("Processing year %d"  %(year))
        for month in range(1, 13):
            progress('.')
            ym = '%4d-%02d' % (year, month)
            for cui_ind,cui in enumerate(cuis):
                # get the count for this cui in this month:
                cur.execute("select count(cui) from cuis INNER JOIN econsults on cuis.row_id = econsults.row_id where cuis.cui=? and date(econsults.date) between date('%s-01') and date('%s-31')" % (ym, ym), (cui,))
                count = cur.fetchone()[0]

                cur.execute('INSERT INTO cui_counts VALUES (?, ?, ?)', (cui, int(count), ym) )
        progress('\n')
    in_conn.commit()
    in_conn.close()

if __name__ == '__main__':
    main(sys.argv[1:])
