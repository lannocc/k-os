from k.ui import *
import k.db as kdb
import k.storage as media
from .core import Resource, Tracker
from .ui import Player as UI, PRACK

from html import escape


class Player(UI):
    def __init__(self, k, source, loop=None, jumps=None):
        video_id = source
        if isinstance(source, Tracker):
            trk = source
            video_id = trk.res.video_id
        else:
            res = Resource(video_id, k.imagine)
            trk = Tracker(res)

        self.video_id = video_id

        self.video = kdb.get_video(video_id)
        self.channel = kdb.get_channel(self.video['channel'])
        thumb = media.get_video_thumbnail(
            self.channel['ytid'], self.video['ytid'])
        thumb = pygame.image.load(thumb)

        super().__init__(k, trk, thumb, loop, jumps)

        self.btn_general = pygame_gui.elements.UIButton(
            text='General',
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((10, 395), (120, 25)))

        self.btn_descr = pygame_gui.elements.UIButton(
            text='Description',
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((10, 420), (120, 25)))

        self.btn_media = pygame_gui.elements.UIButton(
            text='Media',
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((10, 445), (120, 25)))

        self.btn_keywords = pygame_gui.elements.UIButton(
            text='Keywords',
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((10, 470), (120, 25)))

        self.btn_caps = pygame_gui.elements.UIButton(
            text='Captions',
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((10, 495), (120, 25)))

        self.btn_labels = pygame_gui.elements.UIButton(
            text='Labels',
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((10, 520), (120, 25)))

    def kill(self, replace=False):
        super().kill(replace)
        self.trk.res.kill()

    def save(self):
        frag = self.k.frag(kdb.MEDIA_VIDEO, self.video_id, self.trk.begin,
            self.trk.end)
        media.copy_thumbnail(self.video_id, self.k.project(), frag)
        self.k.clip(frag, self.loop, self.loop_begin, self.loop_end, self.jumps)
        self.k.focus_clip(frag)

    def clip(self):
        frag = self.k.frag(kdb.MEDIA_VIDEO, self.video_id, self.loop_begin,
            self.loop_end)
        media.copy_thumbnail(self.video_id, self.k.project(), frag)
        self.k.clip_naked(frag)
        self.k.focus_clip(frag)

    def seq(self):
        frag = self.k.frag(kdb.MEDIA_VIDEO, self.video_id, self.loop_begin,
            self.loop_end)
        media.copy_thumbnail(self.video_id, self.k.project(), frag)
        seg = self.k.seg(frag)
        self.k.focus_seg(seg)

    def click(self, element, target=None):
        if element is self.btn_general:
            self.k.job(self.click_general)

        elif element is self.btn_descr:
            self.k.job(self.click_descr)

        elif element is self.btn_media:
            self.panel_swap(self.btn_media, None)

        elif element is self.btn_keywords:
            self.k.job(self.click_keywords)

        elif element is self.btn_caps:
            self.k.job(self.click_caps)

        elif element is self.btn_labels:
            self.k.job(self.click_labels)

        else:
            return super().click(element, target)

        return True

    def click_general(self):
        self.panel_swap(self.btn_general, General(self))

    def click_descr(self):
        self.panel_swap(self.btn_descr, Description(self))

    def click_keywords(self):
        self.panel_swap(self.btn_keywords, Keywords(self))

    def click_caps(self):
        self.panel_swap(self.btn_caps, Caps(self))

    def click_labels(self):
        self.panel_swap(self.btn_labels, Labels(self))


class General(KPanel):
    def __init__(self, p):
        super().__init__(p.k, None, p.container, PRACK, 1)

        self.lbl_title = pygame_gui.elements.UILabel(
            text='Title:',
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((33, 5), (-1, -1)))

        self.txt_title = pygame_gui.elements.UITextBox(
            html_text=escape(p.video['title']),
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((80, 0), (PRACK[2]-80, 110)))

        self.lbl_author = pygame_gui.elements.UILabel(
            text='Author:',
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((24, 115), (-1, -1)))

        self.txt_author = pygame_gui.elements.UITextEntryLine(
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((80, 110), (PRACK[2]-80, -1)))
        self.txt_author.set_text(p.video['author'])
        self.txt_author.disable()

        self.lbl_length = pygame_gui.elements.UILabel(
            text='Length:',
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((24, 150), (-1, -1)))

        self.txt_length = pygame_gui.elements.UITextEntryLine(
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((80, 145), (80, -1)))
        self.txt_length.set_text(hhmmss(p.video['length']))
        self.txt_length.disable()

        self.lbl_pub = pygame_gui.elements.UILabel(
            text='Published:',
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((180, 150), (-1, -1)))

        self.txt_pub = pygame_gui.elements.UITextEntryLine(
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((260, 145), (PRACK[2]-260, -1)))
        self.txt_pub.set_text(str(p.video['published'].date())) # no time
        self.txt_pub.disable()

        self.lbl_url = pygame_gui.elements.UILabel(
            text='URL:',
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((48, 185), (-1, -1)))

        url = 'https://youtu.be/' + p.video['ytid']
        self.txt_url = pygame_gui.elements.UITextBox(
            html_text=f'<a href="{url}">{url}</a>',
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((80, 180), (PRACK[2]-80, 35)))

        self.lbl_id = pygame_gui.elements.UILabel(
            text='ID:',
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((266, 220), (-1, -1)))

        self.txt_id = pygame_gui.elements.UITextBox(
            html_text=f'<a href="{p.video_id}">{p.video_id}</a>',
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((290, 215), (PRACK[2]-290, 35)))

        self.lbl_ret = pygame_gui.elements.UILabel(
            text='Retrieved:',
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((0, 220), (-1, -1)))

        self.txt_ret = pygame_gui.elements.UITextEntryLine(
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((80, 215), (165, -1)))
        self.txt_ret.set_text(date_time(p.video['retrieved']))
        self.txt_ret.disable()

    def click(self, element, target):
        if element is self.txt_id:
            self.k.focus_video(target)

        else:
            return False

        return True


class Description(KPanel):
    def __init__(self, p):
        super().__init__(p.k, None, p.container, PRACK, 1)

        self.txt = pygame_gui.elements.UITextBox(
            html_text=escape(p.video['description']),
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((0, 0), (PRACK[2], PRACK[3])))


class Keywords(KPanel):
    def __init__(self, p):
        super().__init__(p.k, None, p.container, PRACK, 1)
        self.keywords = kdb.list_keywords(p.video_id)

        html = '<br>'.join([
            f'<a href="{kw["id"]}">' + escape(kw['keyword']) + '</a>' \
            for kw in self.keywords
        ])

        self.txt = pygame_gui.elements.UITextBox(
            html_text=html,
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((0, 0), (PRACK[2], PRACK[3])))

    def click(self, element, target):
        if element is self.txt:
            for keyword in self.keywords:
                if keyword['id'] == int(target):
                    self.k.jab(self.k.focus_keyword, (keyword['keyword'],))
                    break

            return True

        else:
            return False


class Caps(KPanel):
    def __init__(self, p):
        super().__init__(p.k, None, p.container, PRACK, 1)

        self.player = p
        self.caps_id = kdb.id_captions(p.video_id)

        self.btn_filter = None
        self.txt_caps = None
        self.filter = [ ]
        self.txt_fcaps = [ ]

        if self.caps_id:
            self.refresh_inp_filter()

            self.btn_filter = pygame_gui.elements.UIButton(
                text='Filter',
                manager=self.k.gui,
                container=self.container,
                anchors=target(self.inp_filter),
                relative_rect=pygame.Rect((0, 0), (80, 30)))

            html = ' '.join([
                f'<a href="{cap["start"]}">' + escape(cap['txt']) + '</a>' \
                for cap in kdb.list_captions(self.caps_id)
            ])

            self.txt_caps = pygame_gui.elements.UITextBox(
                html_text=html,
                manager=self.k.gui,
                container=self.container,
                relative_rect=pygame.Rect((0, 30), (PRACK[2], PRACK[3]-30)))

        else:
            self.lbl = pygame_gui.elements.UILabel(
                text='No captions for this video.',
                manager=self.k.gui,
                container=self.container,
                relative_rect=pygame.Rect((0, 0), (-1, -1)))

    def refresh_inp_filter(self):
        self.inp_filter = pygame_gui.elements.UITextEntryLine(
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((0, 0), (PRACK[2]-80, 30)))

    def click(self, element, target):
        if element is self.btn_filter:
            if not self.filter:
                txt = self.inp_filter.get_text().strip()
                if txt:
                    self.k.jab(self.do_filter, (txt,))

            else:
                self.filter = [ ]
                txt = self.inp_filter.get_text()
                self.inp_filter.kill() # gets around a gui bug
                self.refresh_inp_filter()
                self.inp_filter.set_text(txt)
                self.btn_filter.set_text('Filter')
                for txt in self.txt_fcaps: txt.kill()
                self.txt_fcaps = [ ]
                self.con_caps.kill()
                self.txt_caps.show()

        elif element is self.txt_caps or element in self.txt_fcaps:
            self.player.seek(int(target) / 1000 * self.player.trk.res.fps)

        else:
            return False

        return True

    def do_filter(self, txt):
        self.filter = list(filter(lambda s: s.strip(), txt.split(' ')))
        self.inp_filter.disable()
        self.btn_filter.set_text('Reset')
        self.txt_caps.hide()

        self.con_caps = pygame_gui.elements.UIScrollingContainer(
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((0, 30), (PRACK[2], PRACK[3]-30)))

        x = 0
        for word in self.filter:
            html = '<br>'.join([
                f'<a href="{caps["start"]}">' + escape(caps['txt']) + '</a> ' \
                for caps in kdb.match_captions(self.caps_id, word)
            ])

            self.txt_fcaps.append(pygame_gui.elements.UITextBox(
                html_text=html,
                manager=self.k.gui,
                container=self.con_caps,
                relative_rect=pygame.Rect((x, 0), (150, 200))))
            x += 150

        self.con_caps.set_scrollable_area_dimensions((x, PRACK[3]-50))


class Labels(KPanel):
    def __init__(self, p):
        super().__init__(p.k, None, p.container, PRACK, 1)
        self.video_id = p.video_id

        self.con_labels = pygame_gui.elements.UIScrollingContainer(
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((0, 0), (PRACK[2], PRACK[3])))

        self.labels = kdb.list_labels()
        self.refresh_video_labels()
        self.buttons = [ ]
        y = 0

        for label in self.labels:
            mark = 'x' if label['id'] in self.video_labels else ' '
            self.buttons.append(pygame_gui.elements.UIButton(
                text=f'[{mark}] {label["name"]}',
                manager=self.k.gui,
                container=self.con_labels,
                relative_rect=pygame.Rect((0, y), (-1, 25))))
            y += 25

        self.con_labels.set_scrollable_area_dimensions((PRACK[2]-20, y))

    def refresh_video_labels(self):
        self.video_labels = [ label['label'] \
            for label in kdb.list_video_labels(self.video_id) ]

    def click(self, element, target=None):
        if element in self.buttons:
            self.k.jab(self.toggle, (element,))
            return True

        else:
            return False

    def toggle(self, button):
        idx = self.buttons.index(button)
        label = self.labels[idx]

        if label['id'] in self.video_labels:
            kdb.delete_label_video(label['id'], self.video_id)
            button.set_text(f'[ ] {label["name"]}')

        else:
            kdb.insert_label_video(label['id'], self.video_id)
            button.set_text(f'[x] {label["name"]}')

        self.refresh_video_labels()

