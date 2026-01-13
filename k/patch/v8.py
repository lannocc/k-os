def patch(cur):
    """
    Apply database schema changes for version 8.

    - Creates the `f_track` table for storing project-scoped F-key audio loops.
    - Adds the `selection_regions` column to the `clip` table for storing
      clip-scoped number-key saved samples.
    """
    cur.execute('''
        CREATE TABLE f_track (
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

    cur.execute('ALTER TABLE clip ADD COLUMN selection_regions TEXT')
