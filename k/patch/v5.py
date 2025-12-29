from datetime import datetime


def patch(cur):
    cur.execute('UPDATE channel SET id = id + 999')

    cur.execute('''
        CREATE TABLE video_new (
            id          INTEGER PRIMARY KEY,
            channel     INTEGER NOT NULL,
            ytid        TEXT NOT NULL UNIQUE,
            author      TEXT,
            title       TEXT,
            description TEXT,
            length      INTEGER,
            published   TIMESTAMP,
            thumb_url   TEXT,
            retrieved   TIMESTAMP,

            FOREIGN KEY (channel) REFERENCES channel (id)
        )
    ''')
    cur.execute('''
        INSERT INTO video_new (
            id,
            channel,
            ytid,
            author,
            title,
            description,
            length,
            published,
            thumb_url,
            retrieved
        )
        SELECT
            id + 999,
            channel + 999,
            ytid,
            author,
            title,
            description,
            length,
            published,
            thumb_url,
            ?
        FROM video
    ''', (
        datetime.now(),
    ))
    cur.execute('DROP TABLE video')
    cur.execute('ALTER TABLE video_new RENAME TO video')

    cur.execute('UPDATE stream SET video = video + 999')
    cur.execute('UPDATE keyword SET video = video + 999')
    cur.execute('UPDATE captions SET video = video + 999')
    cur.execute('UPDATE fragment SET source = source + 999 WHERE media = 10')

    add_channel(cur, 10, 'UCk9H1u4QMFNbBOj96A9DGHw', 'Marcel')
    add_video(cur, 10, 10, 'yJDv-zdhzMY',
        'The Mother of All Demos, presented by Douglas Engelbart (1968)')

    add_channel(cur, 999, 'UC604kMqi2n6y47YLHQ2a8mg', "mix'd k-os")
    add_video(cur, 997, 999, 'I7t1bTgFlyU', 'image engine idles | pygame/k-os')
    add_video(cur, 998, 999, 'm004JwfzCK4',
        '"The sun is gradually expanding" feat. Elex Muscman')
    add_video(cur, 999, 999, 'LpnFGAo3oXs',
        'gen-z fidget spinner... a work in progress')

    cur.execute('''
        CREATE TABLE label (
            id      INTEGER PRIMARY KEY,
            name    TEXT NOT NULL UNIQUE
        )
    ''')

    cur.executemany('''
        INSERT INTO label (
            id,
            name
        )
        VALUES (
            ?, ?
        )
    ''', [
        (9, 'LANNOCC'),
        (420, 'funny'),
        (999, 'k-os'),
    ])

    cur.execute('''
        CREATE TABLE label_video (
            label   INTEGER NOT NULL,
            video   INTEGER NOT NULL,

            PRIMARY KEY (label, video),
            FOREIGN KEY (label) REFERENCES label (id),
            FOREIGN KEY (video) REFERENCES video (id)
        )
    ''')

    cur.executemany('''
        INSERT INTO label_video (
            label,
            video
        )
        VALUES (
            ?, ?
        )
    ''', [
        (9, 10),
        (9, 997),
        (9, 998),
        (9, 999),
        (420, 998),
        (420, 999),
        (999, 997),
        (999, 998),
        (999, 999),
    ])

    # refresh the clip schema (v3 patch)
    cur.execute('''
        CREATE TABLE clip_new (
            fragment    INTEGER PRIMARY KEY,
            name        TEXT,
            key         INTEGER,
            loop        TEXT,
            jumps       TEXT,
            created     TIMESTAMP,
            updated     TIMESTAMP,

            FOREIGN KEY (fragment) REFERENCES fragment (id)
        )
    ''')
    cur.execute('''
        INSERT INTO clip_new (
            fragment,
            name,
            key,
            loop,
            jumps,
            created,
            updated
        )
        SELECT *
        FROM clip
    ''')
    cur.execute('DROP TABLE clip')
    cur.execute('ALTER TABLE clip_new RENAME TO clip')

def add_channel(cur, cid, ytid, name):
    cur.execute('SELECT id FROM channel WHERE ytid = ?', (ytid,))
    existing = cur_fetch(cur)

    if existing:
        eid = existing['id']
        cur.execute('UPDATE video SET channel = ? WHERE channel = ?', (cid,eid))
        cur.execute('UPDATE channel SET id = ? WHERE id = ?', (cid, eid))

    else:
        cur.execute('''
            INSERT INTO channel
            (id, ytid, name)
            VALUES (?, ?, ?)
        ''', (cid, ytid, name))

def add_video(cur, vid, cid, ytid, title):
    cur.execute('SELECT id FROM video WHERE ytid = ?', (ytid,))
    existing = cur_fetch(cur)
    if existing:
        eid = existing['id']
        cur.execute('UPDATE stream SET video = ? WHERE video = ?', (vid, eid))
        cur.execute('UPDATE keyword SET video = ? WHERE video = ?', (vid, eid))
        cur.execute('UPDATE captions SET video = ? WHERE video = ?', (vid, eid))
        cur.execute('UPDATE fragment SET source = ? WHERE media = 10' \
            + ' AND source = ?', (vid, eid))
        #cur.execute('UPDATE label_video SET video = ? WHERE video = ?',
        #    (vid, eid))
        cur.execute('UPDATE video SET id = ?, channel = ? WHERE id = ?',
            (vid, cid, eid))

    else:
        cur.execute('''
            INSERT INTO video
            (id, channel, ytid, title)
            VALUES (?, ?, ?, ?)
        ''', (vid, cid, ytid, title))

def cur_fetch(cur):
    for row in cur:
        return row  # returns first row only

    return None  # if there were no rows

