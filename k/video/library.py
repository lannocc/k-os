from k.ui import *
import k.db as kdb
import k.storage as media
from k.player.video import Player

from html import escape


class Panel(KPanel):
    def __init__(self, k, anchors, container):
        super().__init__(k, anchors, container)

        self.con_channels = None
        self.con_labels = None
        self.con_videos = None

        self.label_filter = [ ]

        #self.lbl_label = pygame_gui.elements.UILabel(
        #    text='Label:',
        #    manager=self.k.gui,
        #    container=self.container,
        #    relative_rect=pygame.Rect((250, 0), (-1, -1)))

        self.lbl_search = pygame_gui.elements.UILabel(
            text='Search:',
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((250, 130), (60, -1)))

        self.inp_search = pygame_gui.elements.UITextEntryLine(
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((310, 125), (190, -1)))

        self.btn_title = pygame_gui.elements.UIButton(
            text='Title',
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((255, 160), (120, 25)))

        self.btn_desc = pygame_gui.elements.UIButton(
            text='Description',
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((375, 160), (120, 25)))

        self.btn_keyword = pygame_gui.elements.UIButton(
            text='Keyword',
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((255, 185), (120, 25)))

        self.btn_captions = pygame_gui.elements.UIButton(
            text='Captions',
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((375, 185), (120, 25)))

        self.refresh()

    def refresh(self, labels=True, visible=False):
        if self.con_channels:
            self.con_channels.kill()
        if self.con_videos:
            self.con_videos.kill()

        self.con_channels = pygame_gui.elements.UIScrollingContainer(
            manager=self.k.gui,
            container=self.container,
            anchors=ANCHOR,
            relative_rect=pygame.Rect((10, 10), (230, 200)))

        self.btn_all_channels = pygame_gui.elements.UIButton(
            text='(all channels)',
            manager=self.k.gui,
            container=self.con_channels.get_container(),
            relative_rect=pygame.Rect((0, 0), (200, 25)))

        self.videos_hidden = [ v['id'] for v in kdb.list_videos_hidden() ]

        self.cur_btn_channel = None
        self.channels = [ ]
        y = 25

        for channel in kdb.list_channels_by_label(self.videos_hidden,
                                                  self.label_filter):
            entry = ChannelEntry(self.k,
                self.con_channels.get_container(), y, channel)
            self.channels.append(entry)
            y += entry.get_rect().height

        self.con_channels.set_scrollable_area_dimensions((200, y))

        if visible:
            self.con_channels.hide()
            self.con_channels.show()

        if labels:
            if self.con_labels:
                self.con_labels.kill()

            self.con_labels = pygame_gui.elements.UIScrollingContainer(
                manager=self.k.gui,
                container=self.container,
                anchors=ANCHOR,
                relative_rect=pygame.Rect((260, 10), (230, 100)))

            self.btn_any_label = pygame_gui.elements.UIButton(
                text='(any label)',
                manager=self.k.gui,
                container=self.con_labels.get_container(),
                relative_rect=pygame.Rect((0, 0), (200, 25)))
            self.btn_any_label.disable()

            self.labels = [ ]
            y = 25

            for label in kdb.list_labels():
                entry = LabelEntry(self.k,
                    self.con_labels.get_container(), y, label)
                self.labels.append(entry)
                y += entry.get_rect().height

            self.con_labels.set_scrollable_area_dimensions((200, y))

            if visible:
                self.con_labels.hide()
                self.con_labels.show()

        self.inp_search.set_text('')

    def refresh_videos(self, channel_id=None, search_title=None,
                       search_description=None, search_keyword=None,
                       search_captions=None):
        if not search_title and not search_description and not search_keyword \
                and not search_captions:
            self.inp_search.set_text('')

        if self.con_videos:
            self.con_videos.kill()

        self.con_videos = pygame_gui.elements.UIScrollingContainer(
            manager=self.k.gui,
            container=self.container,
            anchors=target(self.con_channels, 'top'),
            relative_rect=pygame.Rect((10, 10), (500, 300)))

        self.videos = [ ]
        y = 0

        for video in kdb.list_videos(self.videos_hidden, self.label_filter,
                channel_id, search_title, search_description, search_keyword,
                search_captions):
            entry = VideoEntry(self.k,
                self.con_videos.get_container(), y, video)
            self.videos.append(entry)
            y += entry.get_rect().height

        self.con_videos.set_scrollable_area_dimensions((470, y))

    def refresh_video(self, video_id):
        if self.cur_btn_channel:
            self.cur_btn_channel.enable()
        self.cur_btn_channel = None
        self.inp_search.set_text('')

        if self.con_videos:
            self.con_videos.kill()

        self.con_videos = pygame_gui.elements.UIScrollingContainer(
            manager=self.k.gui,
            container=self.container,
            anchors=target(self.con_channels, 'top'),
            relative_rect=pygame.Rect((10, 10), (500, 300)))

        self.videos = [ ]
        entry = VideoEntry(self.k, self.con_videos.get_container(), 0,
            kdb.list_video(video_id))
        self.videos.append(entry)
        self.con_videos.set_scrollable_area_dimensions(
            (470, entry.get_rect().height))

    def click(self, element, target=None):
        if element == self.btn_all_channels:
            if self.cur_btn_channel:
                self.cur_btn_channel.enable()

            self.cur_btn_channel = self.btn_all_channels
            self.cur_btn_channel.disable()
            self.k.job(self.refresh_videos)

        elif element == self.btn_any_label:
            self.k.job(self.clear_labels)

        elif element == self.btn_title:
            search = self.inp_search.get_text()
            if not search:
                return
            if self.cur_btn_channel:
                self.cur_btn_channel.enable()
            self.cur_btn_channel = None
            self.refresh_videos(search_title=search)

        elif element == self.btn_desc:
            search = self.inp_search.get_text()
            if not search:
                return
            if self.cur_btn_channel:
                self.cur_btn_channel.enable()
            self.cur_btn_channel = None
            self.refresh_videos(search_description=search)

        elif element == self.btn_keyword:
            search = self.inp_search.get_text()
            if not search:
                return
            if self.cur_btn_channel:
                self.cur_btn_channel.enable()
            self.cur_btn_channel = None
            self.refresh_videos(search_keyword=search)

        elif element == self.btn_captions:
            search = self.inp_search.get_text()
            if not search:
                return
            if self.cur_btn_channel:
                self.cur_btn_channel.enable()
            self.cur_btn_channel = None
            self.refresh_videos(search_captions=search)

        else:
            for channel in self.channels:
                channel.click(element, target)

            for label in self.labels:
                label.click(element, target)

            if self.con_videos:
                for video in self.videos:
                    video.click(element, target)

    def clear_labels(self):
        self.label_filter = [ ]
        self.refresh(True, True)


class ChannelEntry(KPanel):
    def __init__(self, k, container, y, channel):
        super().__init__(k, container=container, relative_rect=pygame.Rect(
            (0, y), (200, 25)))

        self.channel_id = channel['id']

        self.btn_name = pygame_gui.elements.UIButton(
            text=channel['name'],
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((0, 0), (200, 25)))

    def click(self, element, target=None):
        if element == self.btn_name:
            panel = self.k.panel_video.panel_library

            if panel.cur_btn_channel:
                panel.cur_btn_channel.enable()

            panel.cur_btn_channel = self.btn_name
            panel.cur_btn_channel.disable()
            self.k.job(self.refresh)

    def refresh(self):
        self.k.panel_video.panel_library.refresh_videos(self.channel_id)


class LabelEntry(KPanel):
    def __init__(self, k, container, y, label):
        super().__init__(k, container=container, relative_rect=pygame.Rect(
            (0, y), (200, 25)))

        self.label_id = label['id']
        self.name = label['name']

        try:
            panel = self.k.panel_video.panel_library
            x = 'x' if self.label_id in panel.label_filter else ' '
        except AttributeError:
            x = ' '

        self.btn_name = pygame_gui.elements.UIButton(
            text=f'[{x}] {self.name}',
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((0, 0), (200, 25)))

    def click(self, element, target=None):
        if element == self.btn_name:
            self.k.job(self.toggle)

    def toggle(self):
        panel = self.k.panel_video.panel_library

        if self.label_id in panel.label_filter:
            idx = panel.label_filter.index(self.label_id)
            del panel.label_filter[idx]
            self.btn_name.set_text(f'[ ] {self.name}')

            if not panel.label_filter:
                panel.btn_any_label.disable()

        else:
            panel.label_filter.append(self.label_id)
            self.btn_name.set_text(f'[x] {self.name}')
            panel.btn_any_label.enable()

        panel.refresh(False, True)


class VideoEntry(KPanel):
    def __init__(self, k, container, y, video):
        super().__init__(k, container=container, relative_rect=pygame.Rect(
            (0, y), (470, 80)), visible=1)

        self.video_id = video['id']
        self.ready = video['retrieved'] is not None

        self.img_thumb = pygame_gui.elements.UIImage(
            image_surface=pygame.image.load(
                media.get_video_thumbnail(video['cytid'], video['ytid'])),
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((0, 0), (100, 75)))

        self.txt_title = pygame_gui.elements.UITextBox(
            html_text=escape(video['title']),
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((100, 0), (290, 75)))

        self.btn_play = pygame_gui.elements.UIButton(
            text=('Play' if self.ready else 'Get'),
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((390, 0), (80, 50)))

        self.btn_delete = pygame_gui.elements.UIButton(
            text='Delete',
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((390, 50), (80, 25)))
        self.btn_delete.disable() #FIXME

    def click(self, element, target=None):
        if element == self.btn_play:
            if self.ready:
                self.k.job(self.play)

            else:
                self.btn_play.set_text('...')
                self.btn_play.disable()
                self.k.job(self._get_, 'D')

    def play(self):
        self.k.player.open(Player(self.k, self.video_id))
        self.k.player.play()

    def _get_(self):
        try:
            media.finish_adding_video(self.video_id)
            self.ready = True
            self.k.job(self._get_audio_, 'B')

        except Exception as e:
            self.btn_play.enable()
            self.btn_play.set_text('!!!')
            raise e

    def _get_audio_(self):
        try:
            media.extract_audio_from_video(self.video_id)
            self.btn_play.enable()
            self.btn_play.set_text('Play')

            print('FINISHED ADDING')

        except Exception as e:
            self.btn_play.enable()
            self.btn_play.set_text('!!!')

