
MEDIA_SEQ = 20

OP_START = 10
OP_STOP = 20
OP_HOLD = 30


def patch(cur):
    cur.execute('DELETE FROM media WHERE id = ?', (MEDIA_SEQ,))

    cur.execute('''
        CREATE TABLE operation (
            id      INTEGER PRIMARY KEY,
            name    TEXT NOT NULL
        )
    ''')

    cur.executemany('''
        INSERT INTO operation (
            id,
            name
        )
        VALUES (
            ?, ?
        )
    ''', [
        (OP_START, 'start'),
        (OP_STOP, 'stop'),
        (OP_HOLD, 'hold'),
    ])

    cur.execute('''
        CREATE TABLE replay (
            id      INTEGER PRIMARY KEY,
            name    TEXT,
            start   INTEGER,
            stop    INTEGER
        )
    ''')

    cur.execute('''
        CREATE TABLE replay_op (
            id          INTEGER PRIMARY KEY,
            replay      INTEGER NOT NULL,
            millis      INTEGER NOT NULL,
            video       INTEGER NOT NULL,
            operation   INTEGER NOT NULL,
            frame       INTEGER NOT NULL,

            FOREIGN KEY (replay) REFERENCES replay (id),
            FOREIGN KEY (video) REFERENCES video (id),
            FOREIGN KEY (operation) REFERENCES operation (id)
        )
    ''')

