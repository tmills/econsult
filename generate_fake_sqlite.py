import random
import sqlite3
import sys

cuis = ['C1234567', 'C0123456', 'C2345678', 'C3456789', 'C4567890']

def create_econsult(cursor, index):
    month = random.randint(1,12)
    day = random.randint(1,28)
    year = random.randint(2010,2017)
    date = '%4d-%02d-%02d' % (year, month, day)

    text = 'This is the text of econsult %d' % (index)
    query = "INSERT INTO econsults VALUES (%d, '%s', '%s')" % (index, date, text)
    cursor.execute(query)

    for cui_ind in range(len(cuis)):
        if random.random() > 0.75:
            query = "INSERT INTO cuis VALUES (%d, '%s')" % (index, cuis[cui_ind])
            cursor.execute(query)



def main(args):
    if len(args) < 1:
        sys.stderr.write('1 required argument: <sqlite filename>\n')
        sys.exit(-1)
    
    conn = sqlite3.connect(args[0])
    c = conn.cursor()

    c.execute('''CREATE TABLE econsults (row_id int, date text, question text)''')
    c.execute('''CREATE TABLE cuis (row_id int, cui text)''')

    for index in range(100000):
        create_econsult(c, index)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    main(sys.argv[1:])

