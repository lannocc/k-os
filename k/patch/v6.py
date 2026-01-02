

def patch(cur):
    cur.execute('''
        CREATE TABLE caption_new (
            id          INTEGER PRIMARY KEY,
            captions    INTEGER NOT NULL,
            start       INTEGER NOT NULL,
            txt         TEXT,

            FOREIGN KEY (captions) REFERENCES captions (id)
        )
    ''')
    cur.execute('INSERT INTO caption_new SELECT * FROM caption')
    cur.execute('DROP TABLE caption')
    cur.execute('ALTER TABLE caption_new RENAME TO caption')

    add_channel(cur, 20, 'UCTdw38Cw6jcm0atBPA39a0Q', 'NDC Conferences')
    add_video(cur, 20, 20, '6avJHaC3C2U', 'The Art of Code - Dylan Beattie')

    add_channel(cur, 30, 'UCMXjSvsqlx1CMoNY-i7Pmyw', 'Space Feather')
    add_video(cur, 30, 30, 'GsDrXc94NGU',
        'On Max Headroom: The Most Misunderstood Joke on TV')

    add_channel(cur, 40, 'UCpwvZwUam-URkxB7g4USKpg', 'RT')
    add_video(cur, 40, 40, 'D95LqdndUM8',
        '‘There Will Be No Winners’ If War Breaks Out - Putin')

    add_channel(cur, 50, 'UCfAOh2t5DpxVrgS9NQKjC7A', 'The Onion')
    add_video(cur, 50, 50, 'vm1U5E44W90',
        'Putin Learns Putin Behind Plot To Assassinate Putin')

    add_channel(cur, 100, 'UCqFzWxSCi39LnW1JKFR3efg', 'Saturday Night Live')
    add_video(cur, 100, 100, 'gaoQ5mMRDhg', 'Shud the Mermaid - SNL')
    add_video(cur, 101, 100, 'XD66suMp3J4', 'Billionaire Star Trek - SNL')

    cur.executemany('''
        INSERT OR IGNORE INTO label_video (label, video)
        VALUES (?, ?)
    ''', [
        (9, 20),
        (9, 30),
        (9, 40),
        (9, 50),
        (9, 100),
        (9, 101),
        (420, 50),
        (420, 100),
        (420, 101),
    ])

    cur.execute('DELETE FROM label_video WHERE label = 9 AND video = 999')
    cur.execute('DELETE FROM label_video WHERE label = 9 AND video = 998')

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
        cur.execute('UPDATE label_video SET video = ? WHERE video = ?',
            (vid, eid))
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

