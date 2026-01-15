from k.ui import *
import k.db as kdb
import k.storage as media
from version import VVHEN

import json
import traceback

# Lazy import tkinter to avoid it being a hard dependency and to manage the root window.
_tk_root = None
def _get_tk_root():
    global _tk_root
    if _tk_root is None:
        try:
            from tkinter import Tk
            _tk_root = Tk()
            _tk_root.withdraw()
        except ImportError:
            print("tkinter not found, file dialogs will not be available.")
            return None
    return _tk_root


class Panel(KPanel):
    def __init__(self, k, anchors, container):
        super().__init__(k, anchors, container)

        self.btn_import = pygame_gui.elements.UIButton(
            text='Import Project...',
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((10, 420), (150, 30)),
            anchors={'left': 'left', 'top': 'top'}
        )
        
        self.con_projects = None
        self.refresh()

    def refresh(self, studio_id=None):
        if self.con_projects:
            self.con_projects.kill()

        self.con_projects = pygame_gui.elements.UIScrollingContainer(
            manager=self.k.gui,
            container=self.container,
            anchors=ANCHOR,
            relative_rect=pygame.Rect((10, 10), (500, 400)))

        self.projects = [ ]
        y = 0

        for project in kdb.list_projects():
            entry = Entry(self.k, self.con_projects.get_container(),
                y, project)
            self.projects.append(entry)
            y += entry.get_rect().height

            if studio_id and entry.project_id == studio_id:
                entry.btn_open.disable()

        self.con_projects.set_scrollable_area_dimensions((480, y))

    def click(self, element, target=None):
        if element == self.btn_import:
            self.k.job(self.import_project)
            return
            
        for entry in self.projects:
            entry.click(element, target)

    def import_project(self):
        from tkinter import filedialog
        
        root = _get_tk_root()
        if not root: return
        
        filepath = filedialog.askopenfilename(
            parent=root,
            title="Import k-os Project",
            filetypes=(("k-os Project", "*.k"), ("All files", "*.*"))
        )
            
        if not filepath:
            return

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                manifest = json.load(f)

            if manifest.get('type') != 'k-os project export':
                print("Error: Not a valid k-os project export file.")
                # TODO: Show an error message to the user via UI
                return

            with kdb.Transaction():
                data = manifest['data']

                # ID maps
                channel_map = {}
                video_map = {}

                # Channels
                for channel in data.get('channels', []):
                    manifest_id = channel['id']
                    local_id = kdb.id_channel(channel['ytid'])
                    if not local_id:
                        kdb.cur.execute('INSERT INTO channel (ytid, name, url) VALUES (?, ?, ?)',
                                        (channel['ytid'], channel['name'], channel['url']))
                        local_id = kdb.cur.lastrowid
                    channel_map[manifest_id] = local_id

                # Videos
                for video in data.get('videos', []):
                    manifest_id = video['id']
                    local_id = kdb.id_video(video['ytid'])
                    if not local_id:
                        local_channel_id = channel_map[video['channel']]
                        kdb.cur.execute('''
                            INSERT INTO video (channel, ytid, author, title, description, length, published, thumb_url, retrieved)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (local_channel_id, video['ytid'], video['author'], video['title'],
                              video['description'], video['length'], video['published'],
                              video['thumb_url'], video['retrieved']))
                        local_id = kdb.cur.lastrowid
                    video_map[manifest_id] = local_id

                # Project
                project_data = data['project']
                kdb.cur.execute('INSERT INTO project (name, created, updated) VALUES (?, ?, ?)',
                                (project_data['name'], project_data['created'], project_data['updated']))
                new_project_id = kdb.cur.lastrowid
                media.start_project(new_project_id)

                # Fragments
                frag_map = {}
                for frag in data.get('fragments', []):
                    manifest_frag_id = frag['id']
                    local_video_id = video_map[frag['source']]
                    kdb.cur.execute('INSERT INTO fragment (project, media, source, start, stop) VALUES (?, ?, ?, ?, ?)',
                                    (new_project_id, frag['media'], local_video_id, frag['start'], frag['stop']))
                    local_frag_id = kdb.cur.lastrowid
                    frag_map[manifest_frag_id] = local_frag_id

                # Clips
                for clip in data.get('clips', []):
                    local_frag_id = frag_map[clip['fragment']]
                    kdb.cur.execute('''
                        INSERT INTO clip (fragment, name, key, loop, jumps, created, updated, selection_regions)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (local_frag_id, clip['name'], clip['key'], clip['loop'], clip['jumps'],
                          clip['created'], clip['updated'], clip.get('selection_regions')))

                # Sequences
                seq_map = {}
                for seq in data.get('sequences', []):
                    manifest_seq_id = seq['id']
                    kdb.cur.execute('INSERT INTO sequence (project, name, created, updated) VALUES (?, ?, ?, ?)',
                                    (new_project_id, seq['name'], seq['created'], seq['updated']))
                    local_seq_id = kdb.cur.lastrowid
                    seq_map[manifest_seq_id] = local_seq_id

                # Segments
                for seg in data.get('segments', []):
                    local_seq_id = seq_map[seg['sequence']]
                    local_frag_id = frag_map[seg['fragment']]
                    kdb.cur.execute('INSERT INTO segment (sequence, idx, fragment) VALUES (?, ?, ?)',
                                    (local_seq_id, seg['idx'], local_frag_id))

                # F-Tracks
                for f_track in data.get('f_tracks', []):
                    music_context = f_track.get('music_context_json')
                    if music_context:
                        mc_data = json.loads(music_context)
                        if 'source_video_id' in mc_data:
                            manifest_video_id = mc_data['source_video_id']
                            mc_data['source_video_id'] = video_map.get(manifest_video_id, manifest_video_id)
                            music_context = json.dumps(mc_data)
                    kdb.upsert_f_track(new_project_id, f_track['fkey'], f_track['actions'],
                                       f_track['duration'], f_track['volume'], f_track['locked'], music_context)

        except Exception as e:
            print("Project import failed.")
            traceback.print_exc()
        finally:
            self.refresh()
            self.hide()
            self.show()


class Entry(KPanel):
    def __init__(self, k, container, y, project):
        super().__init__(k, container=container, relative_rect=pygame.Rect(
            (0, y), (480, 85)))

        self.project_id = project['id']

        name = project['name']
        if not name:
            name = ''

        self.btn_open = pygame_gui.elements.UIButton(
            text='Open',
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((0, 5), (80, 25)))

        self.btn_delete = pygame_gui.elements.UIButton(
            text='Delete',
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((0, 30), (80, 25)))

        self.btn_export = pygame_gui.elements.UIButton(
            text='Export',
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((0, 55), (80, 25)))

        self.lbl_name = pygame_gui.elements.UILabel(
            text=name,
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((90, 0), (390, 20)))

        self.lbl_created = pygame_gui.elements.UILabel(
            text=f'created: {project["created"]}',
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((90, 20), (390, 20)))

        self.lbl_updated = pygame_gui.elements.UILabel(
            text=f'updated: {project["updated"]}',
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((90, 40), (390, 20)))

    def click(self, element, target=None):
        if element == self.btn_open:
            self.btn_open.disable()
            self.k.job(self.open_project)

        elif element == self.btn_delete:
            self.k.confirm(
                self.delete_project,
                'Delete Project?',
                'Delete',
                f'Are you sure you want to delete the project "{self.lbl_name.text}"?'
            )
        
        elif element == self.btn_export:
            self.k.job(self.export_project)

    def open_project(self):
        panel = self.k.panel_project
        panel.panel_studio.open_project(self.project_id)
        panel.panel_swap(panel.btn_studio, panel.panel_studio)

    def delete_project(self):
        panel = self.k.panel_project
        if panel.panel_studio.project_id == self.project_id:
            panel.panel_studio.close_project()
        media.delete_project_folder(self.project_id)
        kdb.delete_project(self.project_id)
        panel.panel_library.refresh()
        panel.panel_library.hide()
        panel.panel_library.show()

    def export_project(self):
        from tkinter import filedialog
        
        root = _get_tk_root()
        if not root: return
        
        filepath = filedialog.asksaveasfilename(
            parent=root,
            title="Export k-os Project",
            defaultextension=".k",
            filetypes=(("k-os Project", "*.k"), ("All files", "*.*"))
        )

        if not filepath:
            return

        try:
            project_id = self.project_id
            data = {}

            data['project'] = kdb.get_project(project_id)
            data['f_tracks'] = kdb.list_f_tracks(project_id)

            kdb.cur.execute('SELECT * FROM fragment WHERE project = ?', (project_id,))
            fragments = kdb.cur_fetchall()
            data['fragments'] = fragments
            
            frag_ids = [f['id'] for f in fragments]
            if frag_ids:
                placeholders = ','.join('?' * len(frag_ids))
                kdb.cur.execute(f'SELECT * FROM clip WHERE fragment IN ({placeholders})', frag_ids)
                data['clips'] = kdb.cur_fetchall()
            else:
                data['clips'] = []

            kdb.cur.execute('SELECT * FROM sequence WHERE project = ?', (project_id,))
            sequences = kdb.cur_fetchall()
            data['sequences'] = sequences

            seq_ids = [s['id'] for s in sequences]
            if seq_ids:
                placeholders = ','.join('?' * len(seq_ids))
                kdb.cur.execute(f'SELECT * FROM segment WHERE sequence IN ({placeholders})', seq_ids)
                data['segments'] = kdb.cur_fetchall()
            else:
                data['segments'] = []

            video_ids = set(f['source'] for f in fragments)
            if video_ids:
                placeholders = ','.join('?' * len(video_ids))
                kdb.cur.execute(f'SELECT * FROM video WHERE id IN ({placeholders})', list(video_ids))
                videos = kdb.cur_fetchall()
                data['videos'] = videos
                
                channel_ids = set(v['channel'] for v in videos)
                if channel_ids:
                    placeholders = ','.join('?' * len(channel_ids))
                    kdb.cur.execute(f'SELECT * FROM channel WHERE id IN ({placeholders})', list(channel_ids))
                    data['channels'] = kdb.cur_fetchall()
                else:
                    data['channels'] = []
            else:
                data['videos'] = []
                data['channels'] = []

            manifest = {
                "type": "k-os project export",
                "version": VVHEN,
                "data": data
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, cls=kdb.StoreEncoder)
            
            print(f"Project {project_id} exported to {filepath}")

        except Exception as e:
            print(f"Project export failed for project {self.project_id}")
            traceback.print_exc()
