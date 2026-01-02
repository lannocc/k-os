from k.ui import *
import k.db as kdb
from k.player.replay import Player


class Panel(KPanel):
    def __init__(self, k, anchors, container):
        super().__init__(k, anchors, container)

        self.con_replays = None
        self.refresh()

    def refresh(self, review_id=None):
        if self.con_replays:
            self.con_replays.kill()

        self.con_replays = pygame_gui.elements.UIScrollingContainer(
            manager=self.k.gui,
            container=self.container,
            anchors=ANCHOR,
            relative_rect=pygame.Rect((10, 10), (500, 400)))

        self.replays = [ ]
        y = 0

        for replay in kdb.list_replays():
            if replay['stop'] is None:
                continue

            entry = Entry(self.k, self.con_replays.get_container(), y, replay)
            self.replays.append(entry)
            y += entry.get_rect().height

            if review_id and entry.replay_id == review_id:
                entry.btn_open.disable()

        self.con_replays.set_scrollable_area_dimensions((480, y))

    def click(self, element, target=None):
        for entry in self.replays:
            entry.click(element, target)


class Entry(KPanel):
    def __init__(self, k, container, y, replay):
        super().__init__(k, container=container, relative_rect=pygame.Rect(
            (0, y), (480, 60)))

        self.replay_id = replay['id']

        name = replay['name']
        if not name:
            name = ''

        #op = kdb.get_replay_first_op(self.replay_id)
        #video = kdb.get_video(op['video'])
        #channel = kdb.get_channel(video['channel'])

        #self.img_thumb = pygame_gui.elements.UIImage(
        #    image_surface=pygame.image.load(
        #        media.get_video_thumbnail(channel['ytid'], video['ytid'])),
        #    manager=k.gui,
        #    container=self.container,
        #    relative_rect=pygame.Rect((0, 0), (100, 75)))

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
            relative_rect=pygame.Rect((90, 0), (390, 20)))

        self.lbl_started = pygame_gui.elements.UILabel(
            text=f'began: {replay["start"]}',
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((90, 20), (390, 20)))

        self.lbl_stopped = pygame_gui.elements.UILabel(
            text=f'ended: {replay["stop"]}',
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((90, 40), (390, 20)))

    def click(self, element, target=None):
        if element == self.btn_open:
            self.btn_open.disable()
            self.k.job(self.open_replay)

    #def play(self):
    #    self.k.player.open(Player(self.k, self.replay_id))
    #    self.k.player.play()

    def open_replay(self):
        panel = self.k.panel_replay
        panel.panel_review.open_replay(self.replay_id)
        panel.panel_swap(panel.btn_review, panel.panel_review)

