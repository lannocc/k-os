from k.ui import *
import k.db as kdb


class Panel(KPanel):
    def __init__(self, k, anchors):
        super().__init__(k, anchors)

        self.lbl_labels = pygame_gui.elements.UILabel(
            text='Labels:',
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((10, 10), (-1, -1)))

        self.con_labels = None

        self.inp_name = pygame_gui.elements.UITextEntryLine(
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((250, 10), (200, -1)))

        self.btn_new = pygame_gui.elements.UIButton(
            text='New',
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((455, 10), (-1, -1)))

        self.entry = None

        self.refresh(visible=False)

    def refresh(self, label_id=None, visible=True):
        if self.con_labels:
            self.con_labels.kill()
        if self.entry:
            self.entry.kill()

        self.con_labels = pygame_gui.elements.UIScrollingContainer(
            manager=self.k.gui,
            container=self.container,
            anchors=ANCHOR,
            relative_rect=pygame.Rect((10, 35), (230, 200)))

        self.labels = [ ]
        y = 0

        for label in kdb.list_labels(True):
            entry = ListEntry(self.k,
                self.con_labels.get_container(), y, label,
                label['id']==label_id, visible)
            self.labels.append(entry)
            y += entry.get_rect().height

        self.con_labels.set_scrollable_area_dimensions((200, y))

        if label_id:
            self.entry = Entry(self.k, self.container, label_id)

    def click(self, element, target=None):
        if element == self.btn_new:
            self.k.job(self.new)

        else:
            for label in self.labels:
                label.click(element, target)

            if self.entry:
                self.entry.click(element, target)

    def new(self):
        name = self.inp_name.get_text()
        if name:
            label_id = kdb.insert_label(name)
            self.inp_name.set_text('')
            self.refresh(label_id)
            self.k.panel_video.panel_library.refresh(labels=True)


class ListEntry(KPanel):
    def __init__(self, k, container, y, label, selected=False, visible=False):
        super().__init__(k, container=container, relative_rect=pygame.Rect(
            (0, y), (200, 25)), visible=(1 if visible else 0))

        self.label_id = label['id']

        self.btn_name = pygame_gui.elements.UIButton(
            text=label['name'],
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((0, 0), (200, 25)))

        if selected:
            self.btn_name.disable()

    def click(self, element, target=None):
        if element == self.btn_name:
            self.k.panel_home.panel_labels.refresh(self.label_id)


class Entry(KPanel):
    def __init__(self, k, container, label_id):
        super().__init__(k, container=container, relative_rect=pygame.Rect(
            (10, 250), (480, 420)), visible=1)

        self.label_id = label_id

        label = kdb.get_label(self.label_id)

        self.lbl_name = pygame_gui.elements.UILabel(
            text=label['name'],
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((0, 0), (480, 25)))

        self.btn_hide = pygame_gui.elements.UIButton(
            text='',
            manager=k.gui,
            container=self.container,
            anchors=target(self.lbl_name, 'top'),
            relative_rect=pygame.Rect((190, 100), (100, 30)))
        self.refresh_hide(label['hide'])

        self.lbl_hide_info = pygame_gui.elements.UILabel(
            text='When selected, hide all videos tagged with this label.',
            manager=k.gui,
            container=self.container,
            anchors=target(self.btn_hide, 'top'),
            relative_rect=pygame.Rect((0, 0), (480, 25)))

        self.btn_remove = pygame_gui.elements.UIButton(
            text='Remove',
            manager=k.gui,
            container=self.container,
            anchors=target(self.lbl_hide_info, 'top'),
            relative_rect=pygame.Rect((200, 100), (80, 30)))

    def refresh_hide(self, hide):
        if hide:
            self.btn_hide.set_text('[x] Hide')

        else:
            self.btn_hide.set_text('[ ] Hide')

        self.hide = hide

    def click(self, element, target=None):
        if element is self.btn_hide:
            self.k.job(self.toggle_hide)

        elif element is self.btn_remove:
            self.k.job(self.remove)

        else:
            return False

        return True

    def toggle_hide(self):
        hide = not self.hide
        kdb.set_label_hide(self.label_id, hide)
        self.refresh_hide(hide)
        self.k.panel_video.panel_library.refresh(labels=True)

    def remove(self):
        count = kdb.count_label_videos(self.label_id)

        if count > 0:
            self.k.confirm(self._remove_, 'Delete Label?', 'Delete',
                'There ' + ('is' if count==1 else 'are') + f' {count} video' \
                + ('s' if count > 1 else '') + ' tagged with this label. ' \
                + 'This will NOT delete the video(s). Are you sure you want ' \
                + 'to remove it?')

        else:
            self._remove_()

    def _remove_(self):
        kdb.delete_label(self.label_id)
        self.k.panel_home.panel_labels.refresh()
        self.k.panel_video.panel_library.refresh(labels=True)

