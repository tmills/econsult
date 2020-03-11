import sys
import json

from flask import Flask, render_template, current_app, g, request

# import pandas as pd
import sqlite3

app = Flask(__name__)
conn = None
cur = None

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('../liver+gastro_2010-2017.sql')
    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

@app.route("/counts")
def index():

    cur = get_db().cursor()
    rows = []
    for year in range(2010, 2017+1):
        for month in range(1, 13):
            year_size = len(cur.execute("select * from econsults where date(date) between date('%4d-%02d-01') and date('%4d-%02d-31')" % (year, month, year, month)).fetchall())
            rows.append({'Date': '%4d-%02d' % (year, month),
                            'Count': year_size})

    cur.close()
    data = {'chart_data':rows}
    return render_template('counts.html', data=data)

@app.route("/cuis")
def cui_counts():
    start_year = int(request.args.get('start_year', default='2010'))
    start_month_in = int(request.args.get('start_month', default='1'))
    end_year = int(request.args.get('end_year', default='2017'))
    end_month_in = int(request.args.get('end_month', default='12'))

    cur = get_db().cursor()

    # First get top 5 counts across all time
    # currently hard-coded at 5 by html
    cur.execute('select cui from (select cui,count(cui) as frequency from cuis group by cui order by -count(cui) limit 5)')
    cuis = []
    for row in cur:
        cuis.append(row[0])
    
    
    # Now get the count for each of these cuis for each month
    rows = []
    for year in range(start_year, end_year+1):
        if year > start_year:
            start_month = 1
        else:
            start_month = start_month_in
        if year < end_year:
            end_month = 12
        else:
            end_month = end_month_in

        for month in range(start_month, end_month):
            ym = '%4d-%02d' % (year, month)
            rows.append({'Date': ym})
            for cui_ind,cui in enumerate(cuis):
                # get the count for this cui in this month:
                # cur.execute("select count(cui) from cuis INNER JOIN econsults on cuis.row_id = econsults.row_id where cuis.cui=? and date(econsults.date) between date('%s-01') and date('%s-31')" % (ym, ym), (cui,))
                cur.execute('select count from cui_counts where cui=? and date=?', (cui,ym))
                # data[ym][cui] = cur.fetchone()[0]
                rows[-1]['CUI%d' %(cui_ind+1)] = cur.fetchone()[0]
                rows[-1]['CUI%dLabel' % (cui_ind+1)] = cui

    data = {'chart_data':rows}
    return render_template('cuis.html', data=data)

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

if __name__ == "__main__":
    # conn = sqlite3.connect('../liver+gastro_2010-2017.sql')
    # cur = conn.cursor()
    app.run(debug=True)
    # close_db()
    # conn = sqlite3.connect(sys.argv[0])
    # cur = conn.cursor()