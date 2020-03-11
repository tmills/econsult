import csv
import econsult.econsult_data
import sqlite3
import sys
from tqdm import tqdm

class CuiData():
    def __init__(self, cui, polarity, uncertainty, generic, historical):
        self.cui = cui
        self.polarity = int(polarity)
        self.uncertainty = int(uncertainty)
        self.generic = 1 if generic == 'True' else 0
        self.historical = int(historical)

def main(args):
    if len(args) < 5:
        sys.stderr.write('5 required arguments: <source directory> <input file formatted string> <start year> <final year> <sqlite filename> [comma-separated specialties]\n')
        sys.exit(-1)
    
    econsult_dir = args[0]
    in_file_fstr = args[1]
    start_year = int(args[2])
    end_year = int(args[3])
    out_filename = args[4]
    specialties = args[5].split(',')

    conn = sqlite3.connect(out_filename)
    c = conn.cursor()

    c.execute('''CREATE TABLE econsults (row_id int, date text)''')
    c.execute('''CREATE TABLE cuis (row_id int, cui text, polarity int, uncertainty int, generic int, historical int)''')

    ## Populate the tables
    for year in range(start_year, end_year+1):
        fn = in_file_fstr % year
        cui_map = {}
        with open(fn) as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for row in csv_reader:
                row_id = int(row['RowId'])
                if not row_id in cui_map:
                    cui_map[row_id] = []
                
                cui_map[row_id].append( CuiData(row['CUI'], row['Polarity'], row['Uncertainty'], row['Generic'], row['Historical']) )

        for specialty in specialties:
            ey = econsult.econsult_data.EconsultYear(econsult_dir, year, specialty)
            for row_ind, row in enumerate(tqdm(ey)):
                # query = "INSERT INTO econsults VALUES (%d, %s, %s)" % (row.row_id, row.creation_date, row.note_text)
                c.execute("INSERT INTO econsults VALUES (?,?)", (row.row_id, row.creation_date))

                if row.row_id in cui_map:
                    for entry in cui_map[row.row_id]:
                        c.execute("INSERT INTO cuis VALUES (?,?,?,?,?,?)", (row.row_id, entry.cui, entry.polarity, entry.uncertainty, entry.generic, entry.historical))
                        # c.execute(query)


    conn.commit()
    conn.close()

if __name__ == '__main__':
    main(sys.argv[1:])

