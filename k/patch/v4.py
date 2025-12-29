

def patch(cur):
    print('!!! WARNING -- PROCEED WITH CAUTION !!!')
    print('    This patch will delete any and all existing replays.')
    print('    Hit <ENTER> to continue...')
    input()

    cur.execute('DROP TABLE replay_op')
    cur.execute('DROP TABLE replay')
    cur.execute('DROP TABLE operation')
    cur.execute('VACUUM')

    cur.execute('''
        CREATE TABLE replay (
            id      INTEGER PRIMARY KEY,
            name    TEXT,
            start   INTEGER,
            stop    INTEGER,
            data    TEXT
        )
    ''')

    cur.execute('''
        CREATE TABLE replay_video (
            replay      INTEGER NOT NULL,
            video       INTEGER NOT NULL,

            PRIMARY KEY (replay, video),
            FOREIGN KEY (replay) REFERENCES replay (id),
            FOREIGN KEY (video) REFERENCES video (id)
        )
    ''')

