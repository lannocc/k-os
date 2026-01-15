import sqlite3
from datetime import datetime
import pickle
from contextlib import AbstractContextManager
from json import JSONEncoder
from base64 import b64encode


VERSION = 8
DATABASE = 'chaos.db'

# meta table entries
META_VERSION = 'db_version'

# media table entries
MEDIA_VIDEO = 10


print(f'base "{DATABASE}" ...')


class Store:
    def __str__(self):
        return f'{self.__class__.__name__} {vars(self)}'

    def __conform__(self, protocol):
        return pickle.dumps(self)


class StoreEncoder(JSONEncoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def default(self, obj):
        if isinstance(obj, Store):
            return vars(obj)

        elif isinstance(obj, bytes):
            return b64encode(obj).decode()

        elif isinstance(obj, datetime):
            return obj.isoformat()

        else:
            return JSONEncoder.default(self, obj)


def pickle_loader(data):
    try: return pickle.loads(data)
    except pickle.UnpicklingError: return data


con = sqlite3.connect(DATABASE, isolation_level=None,
    detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
def dict_row(cursor, row):
    d = { }
    for i, col in enumerate(cursor.description):
        d[col[0]] = row[i]
    return d
#con.row_factory = sqlite3.Row
con.row_factory = dict_row
sqlite3.register_adapter(bool, int)
sqlite3.register_converter('BOOLEAN', lambda v: bool(int(v)))
sqlite3.register_adapter(dict, pickle.dumps)
sqlite3.register_adapter(list, pickle.dumps)
sqlite3.register_adapter(set, pickle.dumps)
sqlite3.register_adapter(Store, pickle.dumps)
sqlite3.register_converter('PICKLE', pickle_loader)
sqlite3.register_converter("TIMESTAMP", lambda v: datetime.fromisoformat(v.decode()))
cur = con.cursor()
#cur.execute('.dbconfig defensive on')
cur.execute('PRAGMA journal_mode=WAL')
cur.execute('PRAGMA synchronous=NORMAL')
cur.execute('PRAGMA temp_store=MEMORY')
#cur.execute('PRAGMA locking_mode=EXCLUSIVE')
cur.execute('PRAGMA foreign_keys=ON')


def cur_fetch():
    for row in cur:
        return row  # returns first row only

    return None  # if there were no rows

def cur_fetchcol(name):
    row = cur_fetch()
    if not row:
        return None

    return row[name]

def cur_fetchall():
    rows = [ ]

    for row in cur:
        rows.append(row)

    return rows

def close():
    cur.execute('VACUUM')
    con.close()


class Transaction(AbstractContextManager):
    def __init__(self):
        super().__init__()

    def __enter__(self):
        cur.execute('BEGIN')
        return self

    def __exit__(self, exc_type=None, exc_value=None, traceback=None):
        if exc_type or exc_value or traceback:
            cur.execute('ROLLBACK')
        else:
            cur.execute('COMMIT')
        return None


###
### META
###

def _is_version_zero_():
    ''' The original database had no meta table, so this function checks for a
        table known to have existed at the time (i.e. channel) and for the lack
        of the meta table. This is done in order to differentiate between a
        brand new database versus an existing pre-meta database.'''

    try:
        cur.execute('SELECT id FROM channel WHERE id < 0')

    except sqlite3.OperationalError:
        return False

    try:
        cur.execute('SELECT name FROM meta WHERE name = 1')
        return False

    except sqlite3.OperationalError:
        return True

_version_zero_ = _is_version_zero_()

cur.execute('''
    CREATE TABLE IF NOT EXISTS meta (
        name    TEXT PRIMARY KEY,
        value   TEXT
    )
''')

cur.executemany('''
    INSERT OR IGNORE INTO meta (
        name,
        value
    )
    VALUES (
        ?, ?
    )
''', [
    (META_VERSION, VERSION if not _version_zero_ else 0),
])

def get_meta(name):
    cur.execute('''
        SELECT value
        FROM meta
        WHERE name = ?
    ''', (
        name,
    ))

    return cur_fetchcol('value')

def set_meta(name, value):
    cur.execute('''
        UPDATE meta
        SET value = ?
        WHERE name = ?
    ''', (
        value,
        name
    ))

def _upgrade_if_needed_():
    v = int(get_meta(META_VERSION))

    if v < VERSION:
        from k.patch import upgrade
        upgrade(DATABASE, close, cur, cur_fetchall,
                set_meta, META_VERSION, v, VERSION)

_upgrade_if_needed_() # pause here and patch the db before continuing


###
### CHANNEL
###

cur.execute('''
    CREATE TABLE IF NOT EXISTS channel (
        id      INTEGER PRIMARY KEY,
        ytid    TEXT NOT NULL UNIQUE,
        name    TEXT,
        url     TEXT
    )
''')

cur.executemany('''
    INSERT OR IGNORE INTO channel (
        id,
        ytid,
        name
    )
    VALUES (
        ?, ?, ?
    )
''', [
    (10, 'UCk9H1u4QMFNbBOj96A9DGHw', 'Marcel'),
    (20, 'UCTdw38Cw6jcm0atBPA39a0Q', 'NDC Conferences'),
    (30, 'UCMXjSvsqlx1CMoNY-i7Pmyw', 'Space Feather'),
    (40, 'UCpwvZwUam-URkxB7g4USKpg', 'RT'),
    (50, 'UCfAOh2t5DpxVrgS9NQKjC7A', 'The Onion'),
    (100, 'UCqFzWxSCi39LnW1JKFR3efg', 'Saturday Night Live'),
    (999, 'UC604kMqi2n6y47YLHQ2a8mg', "mix'd k-os")
])

def insert_channel(channel):
    cur.execute('''
        INSERT INTO channel (
            ytid,
            name,
            url
        ) VALUES (
            ?, ?, ?
        )
    ''', (
        channel.channel_id,
        channel.channel_name,
        channel.vanity_url
    ))

    return cur.lastrowid

def update_channel(channel_id, channel):
    cur.execute('''
        UPDATE channel
        SET
            name = ?,
            url = ?
        WHERE id = ?
    ''', (
        channel.channel_name,
        channel.vanity_url,
        channel_id
    ))

def get_channel(channel_id):
    cur.execute('''
        SELECT *
        FROM channel
        WHERE id = ?
    ''', (
        channel_id,
    ))

    return cur_fetch()

def id_channel(ytid):
    cur.execute('''
        SELECT id
        FROM channel
        WHERE ytid = ?
    ''', (
        ytid,
    ))

    return cur_fetchcol('id')

def list_channels():
    cur.execute('''
        SELECT *
        FROM channel
        ORDER BY name COLLATE NOCASE
    ''')

    return cur_fetchall()

LIST_CHANNELS_SQL = '''
    SELECT
        c.id AS 'id',
        c.ytid AS 'ytid',
        c.name AS 'name',
        c.url AS 'url'
    FROM video v
    LEFT JOIN channel c ON c.id = v.channel
'''

LIST_CHANNELS_SQL_GROUP_BY = '''
    GROUP BY c.id
    ORDER BY c.name COLLATE NOCASE
'''

def list_channels_by_label(hidden=None, labels=None):
    sql = LIST_CHANNELS_SQL
    sep = ' WHERE '
    args = [ ]

    if labels:
        for i in range(len(labels)):
            sql += f' LEFT JOIN label_video l{i}'
            sql += f' ON l{i}.video = v.id AND l{i}.label = ?'
            args.append(labels[i])

        for i in range(len(labels)):
            sql += sep + f'l{i}.video IS NOT NULL'
            sep = ' AND '

    if hidden:
        sql += sep + 'v.id NOT IN (' + ','.join('?'*len(hidden)) + ')'
        sep = ' AND '
        args.extend(hidden)

    sql += LIST_CHANNELS_SQL_GROUP_BY

    cur.execute(sql, tuple(args))

    return cur_fetchall()


###
### VIDEO
###

cur.execute('''
    CREATE TABLE IF NOT EXISTS video (
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

cur.executemany('''
    INSERT OR IGNORE INTO video (
        id,
        channel,
        ytid,
        title
    )
    VALUES (
        ?, ?, ?, ?
    )
''', [
    (10, 10, 'yJDv-zdhzMY',
        'The Mother of All Demos, presented by Douglas Engelbart (1968)'),
    (20, 20, '6avJHaC3C2U', 'The Art of Code - Dylan Beattie'),
    (30, 30, 'GsDrXc94NGU',
        'On Max Headroom: The Most Misunderstood Joke on TV'),
    (40, 40, 'D95LqdndUM8',
        '‘There Will Be No Winners’ If War Breaks Out - Putin'),
    (50, 50, 'vm1U5E44W90',
        'Putin Learns Putin Behind Plot To Assassinate Putin'),
    (100, 100, 'gaoQ5mMRDhg', 'Shud the Mermaid - SNL'),
    (101, 100, 'XD66suMp3J4', 'Billionaire Star Trek - SNL'),
    (997, 999, 'I7t1bTgFlyU', 'image engine idles | pygame/k-os'),
    (998, 999, 'm004JwfzCK4',
        '"The sun is gradually expanding" feat. Elex Muscman'),
    (999, 999, 'LpnFGAo3oXs', 'gen-z fidget spinner... a work in progress')
])

def insert_video(channel_id, video):
    cur.execute('''
        INSERT INTO video (
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
        VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
    ''', (
        channel_id,
        video.video_id,
        video.author,
        video.title,
        video.description,
        video.length,
        video.publish_date,
        video.thumbnail_url,
        datetime.now()
    ))

    return cur.lastrowid

def update_video(video_id, video):
    cur.execute('''
        UPDATE video
        SET
            author = ?,
            title = ?,
            description = ?,
            length = ?,
            published = ?,
            thumb_url = ?,
            retrieved = ?
        WHERE id = ?
    ''', (
        video.author,
        video.title,
        video.description,
        video.length,
        video.publish_date,
        video.thumbnail_url,
        datetime.now(),
        video_id
    ))

def get_video(video_id):
    cur.execute('''
        SELECT *
        FROM video
        WHERE id = ?
    ''', (
        video_id,
    ))

    return cur_fetch()

def id_video(ytid):
    cur.execute('''
        SELECT id
        FROM video
        WHERE ytid = ?
    ''', (
        ytid,
    ))

    return cur_fetchcol('id')

LIST_VIDEOS_SQL = '''
    SELECT
        v.id AS 'id',
        ch.ytid AS 'cytid',
        v.ytid AS 'ytid',
        v.title AS 'title',
        v.retrieved AS 'retrieved'
    FROM video v
    LEFT JOIN channel ch ON ch.id = v.channel
'''

LIST_VIDEOS_SQL_JOIN_EXTRA = '''
    LEFT JOIN captions cap ON cap.video = v.id
    LEFT JOIN keyword k ON k.video = v.id
'''

LIST_VIDEOS_SQL_GROUP_BY = '''
    GROUP BY v.id
    ORDER BY v.title COLLATE NOCASE
'''

def list_video(video_id):
    sql = LIST_VIDEOS_SQL
    sql += ' WHERE v.id = ?'

    cur.execute(sql, (video_id,))
    return cur_fetch()

def list_videos(hidden=None, labels=None, channel_id=None, search_title=None,
                search_description=None, search_keyword=None,
                search_captions=None):

    sql = LIST_VIDEOS_SQL + LIST_VIDEOS_SQL_JOIN_EXTRA

    if labels:
        for i in range(len(labels)):
            sql += f' LEFT JOIN label_video l{i}'
            sql += f' ON l{i}.video = v.id AND l{i}.label = {labels[i]}'

    sep = ' WHERE '
    args = [ ]

    if hidden:
        sql += sep + 'v.id NOT IN (' + ','.join('?'*len(hidden)) + ')'
        sep = ' AND '
        args.extend(hidden)

    if labels:
        for i in range(len(labels)):
            sql += sep + f'l{i}.video IS NOT NULL'
            sep = ' AND '
        sep = ' AND '

    if channel_id is not None:
        sql += sep + 'v.channel = ?'
        sep = ' AND '
        args.append(channel_id)

    if search_title is not None:
        sql += sep + 'v.title LIKE ?'
        sep = ' AND '
        args.append('%' + search_title + '%')

    if search_description is not None:
        sql += sep + 'v.description LIKE ?'
        sep = ' AND '
        args.append('%' + search_description + '%')

    if search_keyword is not None:
        sql += sep + 'k.keyword LIKE ?'
        sep = ' AND '
        args.append('%' + search_keyword + '%')

    if search_captions is not None:
        sql += sep + 'cap.txt LIKE ?'
        sep = ' AND '
        args.append('%' + search_captions + '%')

    sql += LIST_VIDEOS_SQL_GROUP_BY

    cur.execute(sql, tuple(args))

    return cur_fetchall()

def list_videos_hidden():
    cur.execute('''
        SELECT lv.video AS id
        FROM label_video lv
        LEFT JOIN label l ON l.id = lv.label
        WHERE l.hide = 1
    ''')

    return cur_fetchall()


###
### KEYWORD
###

cur.execute('''
    CREATE TABLE IF NOT EXISTS keyword (
        id      INTEGER PRIMARY KEY,
        video   INTEGER NOT NULL,
        keyword TEXT NOT NULL,

        FOREIGN KEY (video) REFERENCES video (id),
        UNIQUE (video, keyword)
    )
''')

def insert_keyword(video_id, keyword):
    cur.execute('''
        INSERT INTO keyword (
            video,
            keyword
        )
        VALUES (
            ?, ?
        )
    ''', (
        video_id,
        keyword
    ))

    return cur.lastrowid

def list_keywords(video_id):
    cur.execute('''
        SELECT id, keyword
        FROM keyword
        WHERE video = ?
        ORDER BY keyword COLLATE NOCASE
    ''', (video_id,))

    return cur_fetchall()


###
### STREAM
###

cur.execute('''
    CREATE TABLE IF NOT EXISTS stream (
        id          INTEGER PRIMARY KEY,
        video       INTEGER NOT NULL,
        itag        INTEGER NOT NULL,
        type        TEXT,
        subtype     TEXT,
        vcodec      TEXT,
        acodec      TEXT,
        resolution  TEXT,
        fps         INTEGER,
        bitrate     INTEGER,
        is_otf      BOOLEAN,
        is_dash     BOOLEAN,
        is_prog     BOOLEAN,
        is_3d       BOOLEAN,
        is_hdr      BOOLEAN,
        is_live     BOOLEAN,

        FOREIGN KEY (video) REFERENCES video (id),
        UNIQUE (video, itag)
    )
''')

def insert_stream(video_id, stream):
    cur.execute('''
        INSERT INTO stream (
            video,
            itag,
            type,
            subtype,
            vcodec,
            acodec,
            resolution,
            fps,
            bitrate,
            is_otf,
            is_dash,
            is_prog,
            is_3d,
            is_hdr,
            is_live
        )
        VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
    ''', (
        video_id,
        stream.itag,
        stream.type,
        stream.subtype,
        stream.video_codec,
        stream.audio_codec,
        stream.resolution,
        stream.fps,
        stream.bitrate,
        stream.is_otf,
        stream.is_dash,
        stream.is_progressive,
        stream.is_3d,
        stream.is_hdr,
        stream.is_live
    ))

    return cur.lastrowid

def list_video_streams(video_id):
    cur.execute('''
        SELECT *
        FROM stream
        WHERE video = ? AND type = 'video'
        ORDER BY resolution
    ''', (
        video_id,
    ))

    return cur_fetchall()


###
### CAPTIONS
###

cur.execute('''
    CREATE TABLE IF NOT EXISTS captions (
        id      INTEGER PRIMARY KEY,
        video   INTEGER NOT NULL,
        lang    INTEGER NOT NULL,
        txt     TEXT,

        FOREIGN KEY (video) REFERENCES video (id),
        UNIQUE (video, lang)
    )
''')

def insert_captions(video_id, captions, text):
    cur.execute('''
        INSERT INTO captions (
            video,
            lang,
            txt
        )
        VALUES (
            ?, ?, ?
        )
    ''', (
        video_id,
        captions.code,
        #captions.xml_captions
        text
    ))

    return cur.lastrowid

def get_captions(video_id):
    cur.execute('''
        SELECT *
        FROM captions
        WHERE video = ?
    ''', (
        video_id,
    ))

    return cur_fetch()

def id_captions(video_id):
    cur.execute('''
        SELECT id
        FROM captions
        WHERE video = ?
    ''', (
        video_id,
    ))

    return cur_fetchcol('id')

cur.execute('''
    CREATE TABLE IF NOT EXISTS caption (
        id          INTEGER PRIMARY KEY,
        captions    INTEGER NOT NULL,
        start       INTEGER NOT NULL,
        txt         TEXT,

        FOREIGN KEY (captions) REFERENCES captions (id)
    )
''')

INSERT_CAPTION_SQL = '''
    INSERT INTO caption (
        captions,
        start,
        txt
    )
    VALUES (
        ?, ?, ?
    )
'''

def insert_caption(captions_id, start, text):
    cur.execute(INSERT_CAPTION_SQL, (
        captions_id,
        start,
        text
    ))

    return cur.lastrowid

def insert_caption_list(caps):
    cur.executemany(INSERT_CAPTION_SQL, caps)

    return cur.rowcount

def list_captions(captions_id):
    cur.execute('''
        SELECT *
        FROM caption
        WHERE captions = ?
        ORDER BY start, id
    ''', (
        captions_id,
    ))

    return cur_fetchall()

def match_captions(captions_id, word):
    sql = '''
        SELECT *
        FROM caption
        WHERE captions = ?
    '''

    rep = '''
        REPLACE(
        REPLACE(
        REPLACE(
        REPLACE(
        REPLACE(
        REPLACE(
        REPLACE(
        REPLACE(
        REPLACE(txt,
            ',', ' '),
            '/', ' '),
            ';', ' '),
            ':', ' '),
            '(', ' '),
            ')', ' '),
            '?', ' '),
            '!', ' '),
            '.', ' ')
    '''

    sql += f' AND ({rep} = ?'
    sql += 3 * f' OR {rep} LIKE ?'
    sql += ') ORDER BY start, id'

    cur.execute(sql, (
        captions_id,
        word,
        f'{word} %',
        f'% {word}',
        f'% {word} %'
    ))

    return cur_fetchall()


###
### PROJECT
###

cur.execute('''
    CREATE TABLE IF NOT EXISTS project (
        id      INTEGER PRIMARY KEY,
        name    TEXT,
        created TIMESTAMP,
        updated TIMESTAMP
    )
''')

def insert_project():
    t = datetime.now()

    cur.execute('''
        INSERT INTO project (
            created,
            updated
        ) VALUES (
            ?, ?
        )
    ''', (
        t, t
    ))

    return cur.lastrowid

def get_project(project_id):
    cur.execute('''
        SELECT *
        FROM project
        WHERE id = ?
    ''', (
        project_id,
    ))

    return cur_fetch()

def list_projects():
    cur.execute('''
        SELECT *
        FROM project
        ORDER BY name COLLATE NOCASE, updated DESC
    ''')

    return cur_fetchall()

def set_project_name(project_id, name):
    cur.execute('''
        UPDATE project
        SET name = ?, updated = ?
        WHERE id = ?
    ''', (
        name,
        datetime.now(),
        project_id
    ))

def touch_project(project_id):
    cur.execute('''
        UPDATE project
        SET updated = ?
        WHERE id = ?
    ''', (
        datetime.now(),
        project_id
    ))

def delete_project(project_id):
    with Transaction():
        # Get IDs of all sequences and fragments in the project
        cur.execute('SELECT id FROM sequence WHERE project = ?', (project_id,))
        seq_ids = [r['id'] for r in cur_fetchall()]
        cur.execute('SELECT id FROM fragment WHERE project = ?', (project_id,))
        frag_ids = [r['id'] for r in cur_fetchall()]

        # Delete all segments that belong to the project's sequences
        if seq_ids:
            seq_placeholders = ','.join('?' for _ in seq_ids)
            cur.execute(f'DELETE FROM segment WHERE sequence IN ({seq_placeholders})', seq_ids)

        # Delete all clips that belong to the project's fragments
        if frag_ids:
            frag_placeholders = ','.join('?' for _ in frag_ids)
            cur.execute(f'DELETE FROM clip WHERE fragment IN ({frag_placeholders})', frag_ids)

        # Now delete the sequences and fragments themselves
        cur.execute('DELETE FROM sequence WHERE project = ?', (project_id,))
        cur.execute('DELETE FROM fragment WHERE project = ?', (project_id,))

        # f_track will be deleted by ON DELETE CASCADE

        # Finally, delete the project
        cur.execute('DELETE FROM project WHERE id = ?', (project_id,))


###
### F_TRACK
###

cur.execute('''
    CREATE TABLE IF NOT EXISTS f_track (
        project             INTEGER NOT NULL,
        fkey                INTEGER NOT NULL,
        actions             TEXT NOT NULL,
        duration            REAL NOT NULL,
        volume              REAL NOT NULL DEFAULT 0.5,
        locked              BOOLEAN NOT NULL DEFAULT 0,
        music_context_json  TEXT,

        PRIMARY KEY (project, fkey),
        FOREIGN KEY (project) REFERENCES project (id) ON DELETE CASCADE
    )
''')

def upsert_f_track(project_id, fkey, actions, duration, volume, locked, music_context_json):
    cur.execute('''
        INSERT OR REPLACE INTO f_track (
            project, fkey, actions, duration, volume, locked, music_context_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (project_id, fkey, actions, duration, volume, locked, music_context_json))

def delete_f_track(project_id, fkey):
    cur.execute('''
        DELETE FROM f_track WHERE project = ? AND fkey = ?
    ''', (project_id, fkey))

def list_f_tracks(project_id):
    cur.execute('''
        SELECT * FROM f_track WHERE project = ?
    ''', (project_id,))
    return cur_fetchall()


###
### MEDIA FRAGMENT
###

cur.execute('''
    CREATE TABLE IF NOT EXISTS media (
        id      INTEGER PRIMARY KEY,
        name    TEXT NOT NULL
    )
''')

cur.executemany('''
    INSERT OR IGNORE INTO media (
        id,
        name
    )
    VALUES (
        ?, ?
    )
''', [
    (MEDIA_VIDEO, 'video'),
])

cur.execute('''
    CREATE TABLE IF NOT EXISTS fragment (
        id      INTEGER PRIMARY KEY,
        project INTEGER NOT NULL,
        media   INTEGER NOT NULL,
        source  INTEGER NOT NULL,
        start   INTEGER,
        stop    INTEGER,

        FOREIGN KEY (project) REFERENCES project (id),
        FOREIGN KEY (media) REFERENCES media (id)
    )
''')

def insert_frag(project_id, media_id, source_id, start, stop):
    cur.execute('''
        INSERT INTO fragment (
            project,
            media,
            source,
            start,
            stop
        )
        VALUES (
            ?, ?, ?, ?, ?
        )
    ''', (
        project_id,
        media_id,
        source_id,
        start,
        stop
    ))

    return cur.lastrowid

def get_frag(frag_id):
    cur.execute('''
        SELECT *
        FROM fragment
        WHERE id = ?
    ''', (
        frag_id,
    ))

    return cur_fetch()


###
### CLIP
###

cur.execute('''
    CREATE TABLE IF NOT EXISTS clip (
        fragment    INTEGER PRIMARY KEY,
        name        TEXT,
        key         INTEGER,
        loop        TEXT,
        jumps       TEXT,
        created     TIMESTAMP,
        updated     TIMESTAMP,
        selection_regions TEXT,

        FOREIGN KEY (fragment) REFERENCES fragment (id)
    )
''')

def insert_clip(frag_id, loop, jumps):
    t = datetime.now()

    cur.execute('''
        INSERT INTO clip (
            fragment,
            loop,
            jumps,
            created,
            updated
        )
        VALUES (
            ?, ?, ?, ?, ?
        )
    ''', (
        frag_id,
        loop,
        jumps,
        t, t
    ))

    return cur.lastrowid

def get_clip(frag_id):
    cur.execute('''
        SELECT *
        FROM clip
        WHERE fragment = ?
    ''', (
        frag_id,
    ))

    return cur_fetch()

CLIP_LIST_SQL = '''
    SELECT
        f.id AS 'id',
        f.project AS 'project',
        f.source AS 'source',
        f.start AS 'start',
        f.stop AS 'stop',
        c.name AS 'name',
        c.key AS 'key',
        c.loop AS 'loop',
        c.jumps AS 'jumps',
        c.selection_regions AS 'selection_regions'
    FROM clip c
    LEFT JOIN fragment f ON f.id = c.fragment
'''
CLIP_LIST_SQL_ORDER = '''
    ORDER BY c.name COLLATE NOCASE, c.updated DESC
'''
def get_clip_listing(frag_id):
    cur.execute(
        CLIP_LIST_SQL + 'WHERE c.fragment = ?',
        (frag_id,))

    return cur_fetch()

def list_clips(project_id):
    cur.execute(
        CLIP_LIST_SQL + 'WHERE f.project = ?' + CLIP_LIST_SQL_ORDER,
        (project_id,))

    return cur_fetchall()

def set_clip_name(frag_id, name):
    cur.execute('''
        UPDATE clip
        SET name = ?
        WHERE fragment = ?
    ''', (
        name,
        frag_id
    ))

def set_clip_key(frag_id, key):
    cur.execute('''
        UPDATE clip
        SET key = ?
        WHERE fragment = ?
    ''', (
        key,
        frag_id
    ))

def set_clip_loop(frag_id, loop):
    cur.execute('''
        UPDATE clip
        SET loop = ?
        WHERE fragment = ?
    ''', (
        loop,
        frag_id
    ))

def set_clip_jumps(frag_id, jumps):
    cur.execute('''
        UPDATE clip
        SET jumps = ?
        WHERE fragment = ?
    ''', (
        jumps,
        frag_id
    ))

def set_clip_selection_regions(frag_id, regions_json):
    cur.execute('''
        UPDATE clip
        SET selection_regions = ?
        WHERE fragment = ?
    ''', (
        regions_json,
        frag_id
    ))

def touch_clip(frag_id):
    cur.execute('''
        UPDATE clip
        SET updated = ?
        WHERE fragment = ?
    ''', (
        datetime.now(),
        frag_id
    ))

def delete_clip(frag_id):
    with Transaction():
        # A fragment might be used in a sequence segment. Delete those first.
        cur.execute('DELETE FROM segment WHERE fragment = ?', (frag_id,))
        # Delete the clip entry.
        cur.execute('DELETE FROM clip WHERE fragment = ?', (frag_id,))
        # Delete the fragment entry.
        cur.execute('DELETE FROM fragment WHERE id = ?', (frag_id,))


###
### SEQUENCE SEGMENT
###

cur.execute('''
    CREATE TABLE IF NOT EXISTS sequence (
        id      INTEGER PRIMARY KEY,
        project INTEGER NOT NULL,
        name    TEXT,
        created TIMESTAMP,
        updated TIMESTAMP,

        FOREIGN KEY (project) REFERENCES project (id)
    )
''')

def insert_sequence(project_id):
    t = datetime.now()

    cur.execute('''
        INSERT INTO sequence (
            project,
            created,
            updated
        )
        VALUES (
            ?, ?, ?
        )
    ''', (
        project_id,
        t, t
    ))

    return cur.lastrowid

def get_sequence(seq_id):
    cur.execute('''
        SELECT *
        FROM sequence
        WHERE id = ?
    ''', (
        seq_id,
    ))

    return cur_fetch()

def list_sequences(project_id):
    cur.execute('''
        SELECT *
        FROM sequence
        WHERE project = ?
        ORDER BY name COLLATE NOCASE, updated DESC
    ''', (
        project_id,
    ))

    return cur_fetchall()

def set_sequence_name(seq_id, name):
    cur.execute('''
        UPDATE sequence
        SET name = ?
        WHERE id = ?
    ''', (
        name,
        seq_id
    ))

def touch_sequence(seq_id):
    cur.execute('''
        UPDATE sequence
        SET updated = ?
        WHERE id = ?
    ''', (
        datetime.now(),
        seq_id
    ))

cur.execute('''
    CREATE TABLE IF NOT EXISTS segment (
        sequence    INTEGER NOT NULL,
        idx         INTEGER NOT NULL,
        fragment    INTEGER NOT NULL,

        PRIMARY KEY (sequence, idx),
        FOREIGN KEY (sequence) REFERENCES sequence (id),
        FOREIGN KEY (fragment) REFERENCES fragment (id)
    )
''')

def insert_segment(seq_id, idx, frag_id):
    cur.execute('''
        INSERT INTO segment (
            sequence,
            idx,
            fragment
        )
        VALUES (
            ?, ?, ?
        )
    ''', (
        seq_id,
        idx,
        frag_id
    ))

    return cur.lastrowid

def get_segment(seq_id, idx):
    cur.execute('''
        SELECT *
        FROM segment
        WHERE sequence = ? AND idx = ?
    ''', (
        seq_id,
        idx
    ))

    return cur_fetch()

SEGMENT_LIST_SQL = '''
    SELECT
        s.sequence AS 'sequence',
        s.idx AS 'idx',
        s.fragment AS 'fragment',
        f.project AS 'project',
        f.source AS 'source',
        f.start AS 'start',
        f.stop AS 'stop'
    FROM segment s
    LEFT JOIN fragment f ON f.id = s.fragment
'''
SEGMENT_LIST_SQL_ORDER = '''
    ORDER BY s.idx
'''
def get_segment_listing(seq_id, idx):
    cur.execute(
        SEGMENT_LIST_SQL + 'WHERE s.sequence = ? AND s.idx = ?',
        (seq_id, idx))

    return cur_fetch()

def list_segments(seq_id):
    cur.execute(
        SEGMENT_LIST_SQL + 'WHERE s.sequence = ?' + SEGMENT_LIST_SQL_ORDER,
        (seq_id,))

    return cur_fetchall()

def get_last_segment_idx(seq_id):
    cur.execute('''
        SELECT idx
        FROM segment
        WHERE sequence = ?
        ORDER BY idx DESC
        LIMIT 1
    ''', (
        seq_id,
    ))

    return cur_fetchcol('idx')

def set_segment_idx(seq_id, old_idx, new_idx):
    cur.execute('''
        UPDATE segment
        SET idx = ?
        WHERE sequence = ? AND idx = ?
    ''', (
        new_idx,
        seq_id,
        old_idx
    ))


###
### REPLAY
###

cur.execute('''
    CREATE TABLE IF NOT EXISTS replay (
        id      INTEGER PRIMARY KEY,
        name    TEXT,
        start   INTEGER,
        stop    INTEGER,
        data    TEXT
    )
''')

def insert_replay(start):
    cur.execute('''
        INSERT INTO replay (
            start
        ) VALUES (
            ?
        )
    ''', (
        start,
    ))

    return cur.lastrowid

def get_replay(replay_id):
    cur.execute('''
        SELECT *
        FROM replay
        WHERE id = ?
    ''', (
        replay_id,
    ))

    return cur_fetch()

def list_replays():
    cur.execute('''
        SELECT
            id,
            name,
            start,
            stop
        FROM replay
        ORDER BY name COLLATE NOCASE, start DESC
    ''')

    return cur_fetchall()

def finish_replay(replay_id, stop, data):
    cur.execute('''
        UPDATE replay
        SET stop = ?, data = ?
        WHERE id = ?
    ''', (
        stop,
        data,
        replay_id
    ))

def set_replay_name(replay_id, name):
    cur.execute('''
        UPDATE replay
        SET name = ?
        WHERE id = ?
    ''', (
        name,
        replay_id
    ))

cur.execute('''
    CREATE TABLE IF NOT EXISTS replay_video (
        replay      INTEGER NOT NULL,
        video       INTEGER NOT NULL,

        PRIMARY KEY (replay, video),
        FOREIGN KEY (replay) REFERENCES replay (id),
        FOREIGN KEY (video) REFERENCES video (id)
    )
''')

def insert_replay_video(replay, video):
    cur.execute('''
        INSERT INTO replay_video (
            replay,
            video
        ) VALUES (
            ?, ?
        )
    ''', (
        replay,
        video
    ))

    return cur.lastrowid

def list_replay_videos(replay_id):
    cur.execute('''
        SELECT *
        FROM replay_video
        WHERE replay = ?
    ''', (
        replay_id,
    ))

    return cur_fetchall()


###
### LABEL
###

cur.execute('''
    CREATE TABLE IF NOT EXISTS label (
        id      INTEGER PRIMARY KEY,
        name    TEXT NOT NULL COLLATE NOCASE UNIQUE,
        hide    BOOLEAN
    )
''')

cur.executemany('''
    INSERT OR IGNORE INTO label (
        id,
        name
    )
    VALUES (
        ?, ?
    )
''', [
    (9, 'LANNOCC'),
    (420, 'funny'),
    (999, 'k-os')
])

def insert_label(name):
    cur.execute('''
        INSERT INTO label (
            name
        )
        VALUES (
            ?
        )
    ''', (
        name,
    ))

    return cur.lastrowid

def get_label(label_id):
    cur.execute('''
        SELECT *
        FROM label
        WHERE id = ?
    ''', (
        label_id,
    ))

    return cur_fetch()

def list_labels(hidden=False):
    sql = '''
        SELECT *
        FROM label
    '''
    if not hidden:
        sql += ' WHERE hide = 0 OR hide IS NULL'
    sql += ' ORDER BY name COLLATE NOCASE'

    cur.execute(sql)

    return cur_fetchall()

def set_label_hide(label_id, hide):
    cur.execute('''
        UPDATE label
        SET hide = ?
        WHERE id = ?
    ''', (
        hide,
        label_id
    ))

def delete_label(label_id):
    cur.execute('''
        DELETE
        FROM label_video
        WHERE label = ?
    ''', (
        label_id,
    ))

    cur.execute('''
        DELETE
        FROM label
        WHERE id = ?
    ''', (
        label_id,
    ))

cur.execute('''
    CREATE TABLE IF NOT EXISTS label_video (
        label   INTEGER NOT NULL,
        video   INTEGER NOT NULL,

        PRIMARY KEY (label, video),
        FOREIGN KEY (label) REFERENCES label (id),
        FOREIGN KEY (video) REFERENCES video (id)
    )
''')

cur.executemany('''
    INSERT OR IGNORE INTO label_video (
        label,
        video
    )
    VALUES (
        ?, ?
    )
''', [
    (9, 10),
    (9, 20),
    (9, 30),
    (9, 40),
    (9, 50),
    (9, 100),
    (9, 101),
    (9, 997),
    (420, 50),
    (420, 100),
    (420, 101),
    (420, 998),
    (420, 999),
    (999, 997),
    (999, 998),
    (999, 999)
])

def count_label_videos(label_id):
    cur.execute('''
        SELECT COUNT(*)
        FROM label_video
        WHERE label = ?
    ''', (
        label_id,
    ))

    return cur_fetch()[0]

def insert_label_video(label_id, video_id):
    cur.execute('''
        INSERT INTO label_video (
            label,
            video
        ) VALUES (
            ?, ?
        )
    ''', (label_id, video_id))

def list_video_labels(video_id):
    cur.execute('''
        SELECT label
        FROM label_video
        WHERE video = ?
    ''', (video_id,))

    return cur_fetchall()

def delete_label_video(label_id, video_id):
    cur.execute('''
        DELETE FROM label_video
        WHERE label = ? AND video = ?
    ''', (label_id, video_id))



print('db ready :-)')

