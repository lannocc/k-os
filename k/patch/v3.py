

def patch(cur):
    cur.execute('ALTER TABLE clip ADD created TIMESTAMP')
    cur.execute('ALTER TABLE clip ADD updated TIMESTAMP')

    cur.execute('''
        CREATE TABLE sequence (
            id      INTEGER PRIMARY KEY,
            project INTEGER NOT NULL,
            name    TEXT,
            created TIMESTAMP,
            updated TIMESTAMP,

            FOREIGN KEY (project) REFERENCES project (id)
        )
    ''')

    cur.execute('''
        CREATE TABLE segment (
            sequence    INTEGER NOT NULL,
            idx         INTEGER NOT NULL,
            fragment    INTEGER NOT NULL,

            PRIMARY KEY (sequence, idx),
            FOREIGN KEY (sequence) REFERENCES sequence (id),
            FOREIGN KEY (fragment) REFERENCES fragment (id)
        )
    ''')

