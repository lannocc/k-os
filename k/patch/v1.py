from os import mkdir, rename, listdir
from os.path import join, isdir
import shutil

FOLDER_OLD = 'downloads'
FOLDER = 'd'
PROJECTS = 'p'

MEDIA_VIDEO = 10
MEDIA_SEQ = 20


def fetchall(cur):
    rows = [ ]

    for row in cur:
        rows.append(row)

    return rows

def get_video_thumbnail(yt_channel_id, yt_video_id):
    return join(FOLDER, yt_channel_id, f'{yt_video_id}.jpg')

def get_frag_thumbnail(project_id, frag_id):
    return join(PROJECTS, str(project_id), f'{frag_id}.jpg')


def patch(cur):
    cur.execute('DROP TABLE noise')
    cur.execute('DROP TABLE fragment')
    cur.execute('DROP TABLE sequence')

    cur.execute('''
        CREATE TABLE media (
            id      INTEGER PRIMARY KEY,
            name    TEXT NOT NULL
        )
    ''')

    cur.executemany('''
        INSERT INTO media (
            id,
            name
        )
        VALUES (
            ?, ?
        )
    ''', [
        (MEDIA_VIDEO, 'video'),
        (MEDIA_SEQ, 'sequence'),
    ])

    cur.execute('''
        CREATE TABLE fragment (
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

    cur.execute('ALTER TABLE clip RENAME TO clip_old')

    cur.execute('''
        CREATE TABLE clip (
            fragment    INTEGER PRIMARY KEY,
            name        TEXT,
            key         INTEGER,
            loop        TEXT,
            jumps       TEXT,

            FOREIGN KEY (fragment) REFERENCES fragment (id)
        )
    ''')

    cur.execute('''
        INSERT INTO fragment (
            id,
            project,
            media,
            source,
            start,
            stop
        )
        SELECT
            id,
            project, ''' + \
            str(MEDIA_VIDEO) + ''',
            video,
            start,
            stop
        FROM clip_old
    ''')

    cur.execute('''
        INSERT INTO clip (
            fragment,
            name,
            key,
            loop,
            jumps
        )
        SELECT
            id,
            name,
            key,
            loop,
            jumps
        FROM clip_old
    ''')

    cur.execute('DROP TABLE clip_old')

    cur.execute('''
        SELECT
            f.id AS 'fragment',
            f.project AS 'project',
            v.ytid AS 'ytid',
            c.ytid AS 'cytid'
        FROM fragment f
        LEFT JOIN video v ON v.id = f.source
        LEFT JOIN channel c ON c.id = v.channel
    ''')

    frags = fetchall(cur)

    if isdir(FOLDER_OLD):
        try:
            rename(FOLDER_OLD, FOLDER)

        except OSError:
            for f in os.listdir(FOLDER_OLD)
                rename(join(FOLDER_OLD, f), join(FOLDER, f))

    elif not isdir(FOLDER):
        mkdir(FOLDER)

    if not isdir(PROJECTS):
        mkdir(PROJECTS)

    for frag in frags:
        folder = join(PROJECTS, str(frag['project']))
        if not isdir(folder):
            mkdir(folder)

        src = get_video_thumbnail(frag['cytid'], frag['ytid'])
        dst = get_frag_thumbnail(frag['project'], frag['fragment'])
        shutil.copyfile(src, dst)

