from k.ui import *
import k.db as kdb
from k.player.sequence import Player


class Panel(KPanel):
    def __init__(self, k, anchors, container):
        super().__init__(k, anchors, container)

        self.con_seqs = None
        self.seqs = [ ]

    def close_project(self):
        if self.con_seqs:
            self.con_seqs.kill()

        self.seqs = [ ]

    def refresh(self, editor_id=None):
        self.close_project()
        #project = self.k.project()
        project = self.k.panel_project.panel_studio.project_id

        if not project:
            if editor_id:
                raise ValueError('we have a sequence id but no project id')
            return

        self.con_seqs = pygame_gui.elements.UIScrollingContainer(
            manager=self.k.gui,
            container=self.container,
            anchors=ANCHOR,
            relative_rect=pygame.Rect((10, 10), (500, 400)))

        y = 0
        for seq in kdb.list_sequences(project):
            entry = Entry(self.k, self.con_seqs.get_container(), y, seq)
            self.seqs.append(entry)
            y += entry.get_rect().height

            if editor_id and entry.seq_id == editor_id:
                entry.btn_open.disable()

        self.con_seqs.set_scrollable_area_dimensions((480, y))

    def click(self, element, target=None):
        for entry in self.seqs:
            entry.click(element, target)


class Entry(KPanel):
    def __init__(self, k, container, y, seq):
        super().__init__(k, container=container, relative_rect=pygame.Rect(
            (0, y), (480, 60)))

        self.seq_id = seq['id']

        name = seq['name']
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
        self.btn_delete.disable() #FIXME

        self.lbl_name = pygame_gui.elements.UILabel(
            text=name,
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((90, 0), (310, 20)))

        self.lbl_created = pygame_gui.elements.UILabel(
            text=f'created {seq["created"]}',
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((90, 20), (310, 20)))

        self.lbl_updated = pygame_gui.elements.UILabel(
            text=f'updated {seq["updated"]}',
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((90, 40), (310, 20)))

        self.btn_play = pygame_gui.elements.UIButton(
            text='Play',
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((400, 5), (80, 50)))

    def click(self, element, target=None):
        if element == self.btn_open:
            self.btn_open.disable()
            self.k.job(self.open_seq)

        elif element == self.btn_play:
            self.play()

    def play(self):
        self.k.player.open(Player(self.k, self.seq_id))
        self.k.player.play()

    def open_seq(self):
        panel = self.k.panel_project.panel_studio.panel_seq
        panel.panel_editor.open_seq(self.seq_id)
        panel.panel_swap(panel.btn_editor, panel.panel_editor)

