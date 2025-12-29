from k.ui import *
#import k.player.noise as kplay
import k.db as kdb
import k.storage as media


class Panel(KPanel):
    def __init__(self, k, anchors, container):
        super().__init__(k, anchors, container)

        self.con_noises = None
        self.refresh()

    def refresh(self):
        if self.con_noises:
            self.con_noises.kill()

        self.con_noises = pygame_gui.elements.UIScrollingContainer(
            manager=self.k.gui,
            container=self.container,
            anchors=ANCHOR,
            relative_rect=pygame.Rect((10, 10), (500, 400)))

        self.noises = []
        y = 0

        for noise in kdb.list_noises():
            entry = Entry(self.k, self.con_noises.get_container(),
                y, noise)
            self.noises.append(entry)
            y += entry.get_rect().height

        self.con_noises.set_scrollable_area_dimensions((480, y))

    def add_noise(self, video_id, begin, end):
        noise_id = kdb.add_noise(video_id, begin, end)
        self.refresh()
        #player = kplay.Library(self.k, noise_id)
        #self.k.player.open(player)
        #player.hide() #FIXME
        #player.show()
        #player.play()

    def click(self, element, target=None):
        for entry in self.noises:
            entry.click(element, target)


class Entry(KPanel):
    def __init__(self, k, container, y, noise):
        super().__init__(k, container=container, relative_rect=pygame.Rect(
            (0, y), (480, 80)))

        self.noise_id = noise['id']

        name = noise['name']
        if not name:
            name = ''

        self.img_thumb = pygame_gui.elements.UIImage(
            image_surface=pygame.image.load(
                media.get_video_thumbnail(noise['cytid'], noise['ytid'])),
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((0, 0), (100, 75)))

        self.lbl_name = pygame_gui.elements.UILabel(
            text=name,
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((100, 0), (300, 25)))

        self.lbl_created = pygame_gui.elements.UILabel(
            text=f'created {noise["created"]}',
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((100, 25), (300, 25)))

        self.lbl_updated = pygame_gui.elements.UILabel(
            text=f'updated {noise["updated"]}',
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((100, 50), (300, 25)))

        self.btn_play = pygame_gui.elements.UIButton(
            text='Play',
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((400, 0), (80, 25)))

        self.btn_info = pygame_gui.elements.UIButton(
            text='Info',
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((400, 25), (80, 25)))
        self.btn_info.disable() #FIXME

        self.btn_delete = pygame_gui.elements.UIButton(
            text='Delete',
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((400, 50), (80, 25)))
        self.btn_delete.disable() #FIXME

    def click(self, element, target=None):
        if element == self.btn_play:
            p = player.noise.Library(self.k, self.noise_id)
            self.k.player.open(p)
            p.hide() #FIXME
            p.show()
            p.play()

