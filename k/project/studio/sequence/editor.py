from k.ui import *
import k.db as kdb
import k.storage as media
from k.player.segment import Player


class Panel(KPanel):
    def __init__(self, k, anchors, container):
        super().__init__(k, anchors, container)

        self.seq_id = None

        self.btn_close = pygame_gui.elements.UIButton(
            text='X',
            manager=k.gui,
            container=self.container,
            anchors=ANCHOR,
            relative_rect=SPACER)
        self.btn_close.disable()

        self.inp_name = pygame_gui.elements.UITextEntryLine(
            manager=k.gui,
            container=self.container,
            anchors=target(self.btn_close),
            relative_rect=pygame.Rect((10, 10), (370, -1)))

        self.btn_name = pygame_gui.elements.UIButton(
            text='Name',
            manager=k.gui,
            container=self.container,
            anchors=target(self.inp_name),
            relative_rect=SPACER)

        self.con_segs = None
        self.segs = [ ]

    def init_seq(self):
        if self.seq_id:
            kdb.touch_sequence(self.seq_id)

        else:
            project = self.k.project()
            self.seq_id = kdb.insert_sequence(project)
            #media.start_sequence(project, self.seq_id)
            self.k.panel_project.panel_studio.panel_seq.panel_library.refresh(
                self.seq_id)
            self.btn_close.enable()

            self.con_segs = pygame_gui.elements.UIScrollingContainer(
                manager=self.k.gui,
                container=self.container,
                anchors=target(self.btn_name, 'top'),
                relative_rect=pygame.Rect((10, 10), (480, 325)))

        return self.seq_id

    def open_seq(self, seq_id):
        self.close_seq()
        seq = kdb.get_sequence(seq_id)

        self.seq_id = seq_id
        self.btn_close.enable()

        name = seq['name']
        if name:
            self.inp_name.set_text(name)

        self.k.panel_project.panel_studio.panel_seq.panel_library.refresh(
            self.seq_id)

        self.con_segs = pygame_gui.elements.UIScrollingContainer(
            manager=self.k.gui,
            container=self.container,
            anchors=target(self.btn_name, 'top'),
            relative_rect=pygame.Rect((10, 10), (480, 325)))

        y = 0
        for seg in kdb.list_segments(self.seq_id):
            entry = Entry(self.k, self.con_segs.get_container(), y, seg)
            self.segs.append(entry)
            y += entry.get_rect().height

        if self.segs:
            self.segs[0].btn_up.disable()
            self.segs[0].btn_top.disable()
            self.segs[-1].btn_down.disable()
            self.segs[-1].btn_bottom.disable()

        self.con_segs.set_scrollable_area_dimensions((460, y))

    def close_seq(self):
        self.btn_close.disable()
        self.inp_name.set_text('')

        if self.con_segs:
            self.con_segs.kill()
            self.con_segs = None
            self.segs = [ ]

        self.k.panel_project.panel_studio.panel_seq.panel_library.refresh()

    def add_seg(self, idx):
        seg = kdb.get_segment_listing(self.seq_id, idx)

        y = 0
        for entry in self.segs:
            y += entry.get_rect().height

        entry = Entry(self.k, self.con_segs.get_container(), y, seg)
        y += entry.get_rect().height

        entry.btn_down.disable()
        entry.btn_bottom.disable()
        if not self.segs:
            entry.btn_up.disable()
            entry.btn_top.disable()
        else:
            self.segs[-1].btn_down.enable()
            self.segs[-1].btn_bottom.enable()

        self.segs.append(entry)

        self.con_segs.set_scrollable_area_dimensions((460, y))
        scroll_to_bottom(self.con_segs)

    def seg_swap(self, idx_a, idx_b):
        #print(f'swap: {idx_a}, {idx_b}')
        seg_a = self.segs[idx_a]
        seg_b = self.segs[idx_b]

        kdb.set_segment_idx(self.seq_id, idx_a, -1)
        kdb.set_segment_idx(self.seq_id, idx_b, idx_a)
        kdb.set_segment_idx(self.seq_id, -1, idx_b)

        seg_a.idx = idx_b
        seg_b.idx = idx_a

        y_a = seg_a.get_rect().y
        y_b = seg_b.get_rect().y

        seg_a.set_position((0, y_b))
        seg_b.set_position((0, y_a))

        self.segs[idx_a], self.segs[idx_b] = seg_b, seg_a

        self.seg_buttons(seg_a)
        self.seg_buttons(seg_b)

        kdb.touch_sequence(self.seq_id)

    def seg_top(self, idx):
        kdb.set_segment_idx(self.seq_id, idx, -1)
        oseg = self.segs[idx]
        h = oseg.get_rect().height

        for seg in reversed(self.segs[:idx]):
            kdb.set_segment_idx(self.seq_id, seg.idx, seg.idx + 1)
            seg.idx += 1
            seg.move_by(0, h)

        oseg.idx = 0
        kdb.set_segment_idx(self.seq_id, -1, oseg.idx)
        oseg.set_position((0, 0))

        self.seg_buttons(oseg)
        self.seg_buttons(self.segs[0])

        del self.segs[idx]
        self.segs.insert(0, oseg)

        self.seg_buttons(self.segs[idx])

        kdb.touch_sequence(self.seq_id)

    def seg_bottom(self, idx):
        kdb.set_segment_idx(self.seq_id, idx, -1)
        oseg = self.segs[idx]
        h = oseg.get_rect().height

        for seg in self.segs[idx+1:]:
            kdb.set_segment_idx(self.seq_id, seg.idx, seg.idx - 1)
            seg.idx -= 1
            seg.move_by(0, -1*h)

        oseg.idx = len(self.segs) - 1
        kdb.set_segment_idx(self.seq_id, -1, oseg.idx)
        rect = self.segs[-1].get_rect()
        oseg.set_position((0, rect.y + rect.height))

        self.seg_buttons(oseg)
        self.seg_buttons(self.segs[-1])
        
        del self.segs[idx]
        self.segs.append(oseg)

        self.seg_buttons(self.segs[idx])

        kdb.touch_sequence(self.seq_id)

    def seg_buttons(self, seg):
        idx = seg.idx
        top = True if idx==0 else False
        bot = True if idx==len(self.segs)-1 else False

        if top:
            seg.btn_up.disable()
            seg.btn_top.disable()
        else:
            seg.btn_up.enable()
            seg.btn_top.enable()

        if bot:
            seg.btn_down.disable()
            seg.btn_bottom.disable()
        else:
            seg.btn_down.enable()
            seg.btn_bottom.enable()

    def click(self, element, target=None):
        if element == self.btn_close:
            self.close_seq()

        elif element == self.btn_name:
            self.init_seq()
            kdb.set_sequence_name(self.seq_id, self.inp_name.get_text())
            self.k.panel_project.panel_studio.panel_seq.panel_library.refresh(
                self.seq_id)

        else:
            for entry in self.segs:
                if entry.click(element, target):
                    break


class Entry(KPanel):
    def __init__(self, k, container, y, seg):
        super().__init__(k, container=container, relative_rect=pygame.Rect(
            (0, y), (460, 65)))

        self.seq_id = seg['sequence']
        self.idx = seg['idx']
        self.frag_id = seg['fragment']

        self.btn_up = pygame_gui.elements.UIButton(
            text='Up',
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((0, 0), (45, 30)))

        self.btn_down = pygame_gui.elements.UIButton(
            text='Dn',
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((0, 30), (45, 30)))

        self.btn_top = pygame_gui.elements.UIButton(
            text='Top',
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((45, 0), (55, 30)))

        self.btn_bottom = pygame_gui.elements.UIButton(
            text='Bot',
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((45, 30), (55, 30)))

        self.img_thumb = pygame_gui.elements.UIImage(
            image_surface=pygame.image.load(
                media.get_frag_thumbnail(seg['project'], seg['fragment'])),
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((100, 0), (80, 60)))

        self.lbl_range = pygame_gui.elements.UILabel(
            text=f'{seg["start"]} - {seg["stop"]}',
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((180, 10), (200, 20)))

        self.lbl_length = pygame_gui.elements.UILabel(
            text=str(seg['stop']-seg['start']),
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((180, 30), (200, 20)))

        self.btn_play = pygame_gui.elements.UIButton(
            text='Play',
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((380, 0), (80, 25)))

        self.btn_remove = pygame_gui.elements.UIButton(
            text='Remove',
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((380, 25), (80, 25)))
        self.btn_remove.disable() #FIXME

    def click(self, element, target=None):
        editor = self.k.panel_project.panel_studio.panel_seq.panel_editor

        if element == self.btn_play:
            self.play()
            return True

        elif element == self.btn_up:
            editor.seg_swap(self.idx, self.idx - 1)
            return True

        elif element == self.btn_down:
            editor.seg_swap(self.idx, self.idx + 1)
            return True

        elif element == self.btn_top:
            editor.seg_top(self.idx)
            return True

        elif element == self.btn_bottom:
            editor.seg_bottom(self.idx)
            return True

        else:
            return False

    def play(self):
        self.k.player.open(Player(self.k, self.seq_id, self.idx))
        self.k.player.play()

