from k.ui import *
import k.db as kdb
import k.storage as media

from pytube import YouTube, Channel, Playlist, Search
from pytube.exceptions import *

from urllib.request import urlretrieve


YT_RESULT_HEIGHT = 100


class Panel(KPanel):
    def __init__(self, k, anchors, container):
        super().__init__(k, anchors, container)

        self.btn_clear = pygame_gui.elements.UIButton(
            text='X',
            manager=k.gui,
            container=self.container,
            anchors=ANCHOR,
            relative_rect=SPACER)

        self.btn_paste = pygame_gui.elements.UIButton(
            text='P',
            manager=k.gui,
            container=self.container,
            anchors=target(self.btn_clear),
            relative_rect=pygame.Rect((0, 10), (-1, -1)))

        self.input = pygame_gui.elements.UITextEntryLine(
            manager=k.gui,
            container=self.container,
            anchors=target(self.btn_paste),
            relative_rect=pygame.Rect((10, 10), (420, -1)))

        self.btn_video = pygame_gui.elements.UIButton(
            text='Video',
            manager=k.gui,
            container=self.container,
            anchors=target(self.input, 'top', target(self.btn_paste)),
            relative_rect=SPACER)

        self.btn_channel = pygame_gui.elements.UIButton(
            text='Channel',
            manager=k.gui,
            container=self.container,
            anchors=target(self.input, 'top', target(self.btn_video)),
            relative_rect=SPACER)

        self.btn_playlist = pygame_gui.elements.UIButton(
            text='Playlist',
            manager=k.gui,
            container=self.container,
            anchors=target(self.input, 'top', target(self.btn_channel)),
            relative_rect=SPACER)

        self.btn_search = pygame_gui.elements.UIButton(
            text='Search',
            manager=k.gui,
            container=self.container,
            anchors=target(self.input, 'top', target(self.btn_playlist)),
            relative_rect=SPACER)

        self.results = None
        self.ytresults = None

    def click(self, element, target=None):
        if element == self.btn_clear:
            self.clear_results()
            self.input.set_text('')
            self.input.focus()

        elif element == self.btn_paste:
            for scrap in pygame.scrap.get_types():
                if scrap.startswith('text/'):
                    data = pygame.scrap.get(scrap)
                    if isinstance(data, bytes):
                        text = data.decode()
                    else:
                        text = str(data)

                    self.input.set_text(text)
                    self.input.focus()
                    break

        elif element == self.btn_video:
            self.btn_video.disable()
            self.k.job(self.get_video, 'D')

        elif element == self.btn_channel:
            self.btn_channel.disable()
            self.k.job(self.get_channel, 'D')

        elif element == self.btn_playlist:
            self.btn_playlist.disable()
            self.k.job(self.get_playlist, 'D')

        elif element == self.btn_search:
            self.btn_search.disable()
            self.k.job(self.get_search, 'D')

        elif self.ytresults:
            for result in self.ytresults:
                result.click(element, target)

    def get_video(self):
        self.clear_results()
        url = self.input.get_text()
        try:
            yt = YouTube(url)
            self.show_results([yt])

        except PytubeError:
            print('check video url')

        self.btn_video.enable()

    def get_channel(self):
        self.clear_results()
        url = self.input.get_text()
        try:
            yt = Channel(url)
            self.show_results(yt.videos)

        except PytubeError:
            print('check channel url')

        self.btn_channel.enable()

    def get_playlist(self):
        self.clear_results()
        url = self.input.get_text()
        try:
            yt = Playlist(url)
            self.show_results(yt.videos)

        except PytubeError:
            print('check playlist url')

        except KeyError:
            print('check playlist url')

        self.btn_playlist.enable()

    def get_search(self):
        self.clear_results()
        query = self.input.get_text()
        try:
            yt = Search(query)
            self.show_results(yt.results)

        except PytubeError:
            print('something went wrong')

        self.btn_search.enable()

    def clear_results(self):
        if self.results:
            self.ytresults = None
            self.results.kill()
            self.results = None

    def show_results(self, videos):
        self.results = pygame_gui.elements.UIScrollingContainer(
            manager=self.k.gui,
            container=self.container,
            anchors=target(self.btn_search, 'top'),
            relative_rect=pygame.Rect((10, 10), (500, 400)))

        self.results.set_scrollable_area_dimensions((480,
            YT_RESULT_HEIGHT*len(videos)))

        self.ytresults = []
        row = 0

        for video in videos:
            #print(video)
            self.ytresults.append(Entry(self.k,
                self.results.get_container(),
                pygame.Rect((9, row*YT_RESULT_HEIGHT), (480, YT_RESULT_HEIGHT)),
                video, row))
            row+=1


class Entry(KPanel):
    def __init__(self, k, container, relative_rect, video, index):
        super().__init__(k, container=container,
            relative_rect=relative_rect, visible=1)

        self.video_id = None
        self.video = video
        self.thumb = f'/tmp/k-os.thumb-{index}' #FIXME
        urlretrieve(video.thumbnail_url, self.thumb)

        self.lbl_name = pygame_gui.elements.UILabel(
            text=video.title,
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((0, 0), (480, -1)))

        self.img_thumb = pygame_gui.elements.UIImage(
            image_surface=pygame.image.load(self.thumb),
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((0, 25), (100, 75)))

        self.lbl_author = pygame_gui.elements.UILabel(
            text=video.author,
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((100, 30), (280, -1)))

        self.lbl_published = pygame_gui.elements.UILabel(
            text=str(video.publish_date.date()),
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((100, 50), (280, -1)))

        self.lbl_runtime = pygame_gui.elements.UILabel(
            text=hhmmss(video.length),
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((100, 75), (280, -1)))

        self.btn_add = pygame_gui.elements.UIButton(
            text='Get',
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((380, 25), (88, 75)))

        self.video_id = kdb.id_video(video.video_id)
        if self.video_id:
            self.btn_add.set_text('Show')

    def click(self, element, target=None):
        if element == self.btn_add:
            if not self.video_id:
                self.btn_add.set_text('...')
                self.btn_add.disable()
                self.k.job(self._get_, 'D')

            else:
                self.k.focus_video(self.video_id)

    def _get_(self):
        #print(f'video: {self.video}')
        try:
            self.video_id = media.add_video_to_library(self.video)
            self.k.job(self._get_audio_, 'B')

        except Exception as e:
            self.btn_add.enable()
            self.btn_add.set_text('!!!')
            raise e

    def _get_audio_(self):
        try:
            media.extract_audio_from_video(self.video_id)
            self.k.panel_video.panel_library.refresh()
            self.btn_add.enable()
            self.btn_add.set_text('Show')

            print('FINISHED ADDING')

        except Exception as e:
            self.btn_add.enable()
            self.btn_add.set_text('!!!')
            raise e

