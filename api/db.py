import csv
class Database:
    def __init__(self, db_csv="db/db.csv"):
        self.rows = []
        with open(db_csv, 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            fields = next(csvreader)
            for row in csvreader:
                self.rows.append({
                    'title': row[0],
                    'composer': row[1], 
                    'perfomer': row[2],
                    'path' : 'db/' + row[0].lower().replace(" ", "_") + '/' + row[2].lower() + ".mp3"
                })
        print(self.rows)