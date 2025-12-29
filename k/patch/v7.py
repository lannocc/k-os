

def patch(cur):
    cur.execute('''
        CREATE TABLE label_new (
            id      INTEGER PRIMARY KEY,
            name    TEXT NOT NULL UNIQUE COLLATE NOCASE,
            hide    BOOLEAN
        )
    ''')
    cur.execute('''
        INSERT INTO label_new (id, name)
        SELECT id, name FROM label
    ''')
    cur.execute('DROP TABLE label')
    cur.execute('ALTER TABLE label_new RENAME TO label')

