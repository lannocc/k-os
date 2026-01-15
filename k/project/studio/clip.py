from k.ui import *
import k.db as kdb
import k.storage as media
#import k.player.engine as kpengine
#import k.player.project as kplaystud
from k.player.frag import Chaos as Player


class Panel(KPanel):
    def __init__(self, k, anchors, container):
        super().__init__(k, anchors, container)

        self.con_clips = None
        self.clips = []

    def refresh_clips(self):
        if self.con_clips:
            self.con_clips.kill()

        self.con_clips = pygame_gui.elements.UIScrollingContainer(
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((0, 0), (500, 400)))

        self.clips = []
        y = 0

        for clip in kdb.list_clips(
                self.k.panel_project.panel_studio.project_id):
            entry = Entry(self.k, self.con_clips.get_container(),
                y, clip)
            self.clips.append(entry)
            y += entry.get_rect().height

        self.con_clips.set_scrollable_area_dimensions((480, y))

    def close_project(self):
        for entry in self.clips:
            entry.kill()
        self.clips = []

        if self.con_clips:
            self.con_clips.kill()
            self.con_clips = None

    def enable(self):
        for entry in self.clips:
            entry.enable()

    def disable(self):
        for entry in self.clips:
            entry.disable()

    def add_clip(self, clip_id):
        clip = kdb.get_clip_listing(clip_id)

        entry = Entry(self.k, self.con_clips.get_container(), 0, clip)
        self.clips.insert(0, entry)
        dy = entry.get_rect().height
        y = dy

        for entry in self.clips[1:]:
            entry.move_by(0, dy)
            y += entry.get_rect().height

        self.con_clips.set_scrollable_area_dimensions((480, y))

        #entry.play()

    def remove_clip(self, clip):
        project_id = self.k.panel_project.panel_studio.project_id
        if project_id:
            media.delete_frag_thumbnail(project_id, clip.clip_id)

        kdb.delete_clip(clip.clip_id)

        height = clip.get_rect().height
        try:
            clip_index = self.clips.index(clip)
        except ValueError:
            return  # Clip not found, nothing to do

        # Kill UI element and remove from list
        clip.kill()
        self.clips.pop(clip_index)

        # Shift all subsequent clip UIs up
        for i in range(clip_index, len(self.clips)):
            self.clips[i].move_by(0, -height)

        # Update the scrollable area's dimensions
        if self.clips:
            new_height = self.clips[-1].get_rect().bottom
        else:
            new_height = 0
        self.con_clips.set_scrollable_area_dimensions((480, new_height))

    def click(self, element, target=None):
        for entry in self.clips:
            entry.click(element, target)


class Entry(KPanel):
    def __init__(self, k, container, y, clip):
        super().__init__(k, container=container, relative_rect=pygame.Rect(
            (0, y), (470, 60)), visible=1)

        self.clip_id = clip['id']
        self.key = clip['key']
        self.loop = clip['loop']
        self.jumps = clip['jumps']
        self.selection_regions = clip.get('selection_regions')

        if self.key:
            self.k.panel_project.panel_studio.keys[self.key] = self

        self.inp_key = pygame_gui.elements.UITextEntryLine(
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((0, 0), (50, 30)))

        self.inp_key.set_text_length_limit(1)
        if self.key:
            self.inp_key.set_text(chr(self.key))

        self.btn_key = pygame_gui.elements.UIButton(
            text='Key',
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((25, 30), (50, 30)))

        self.img_thumb = pygame_gui.elements.UIImage(
            image_surface=pygame.image.load(
                media.get_frag_thumbnail(clip['project'], clip['id'])),
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((80, 0), (80, 60)))

        self.inp_name = pygame_gui.elements.UITextEntryLine(
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((165, 0), (155, 30)))

        if clip['name']:
            self.inp_name.set_text(clip['name'])

        self.btn_name = pygame_gui.elements.UIButton(
            text='Name',
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((325, 0), (60, 30)))

        self.lbl_range = pygame_gui.elements.UILabel(
            text=f'{clip["start"]} - {clip["stop"]}',
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((165, 35), (155, 20)))

        self.lbl_length = pygame_gui.elements.UILabel(
            text=str(clip['stop']-clip['start']),
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((325, 35), (60, 20)))

        self.btn_play = pygame_gui.elements.UIButton(
            text='Play',
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((390, 0), (80, 25)))

        self.btn_remove = pygame_gui.elements.UIButton(
            text='Remove',
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((390, 25), (80, 25)))

        #self.res = kpengine.Resource(clip['video'])
        #self.player = player.Video(self.k, self.clip_id, True)

    def kill(self):
        #self.player.kill()
        #self.res.kill()

        if self.key:
            del self.k.panel_project.panel_studio.keys[self.key]

        super().kill()

    def enable(self):
        self.btn_remove.enable()
        self.inp_name.enable()
        self.btn_name.enable()
        self.inp_key.enable()
        self.btn_key.enable()

    def disable(self):
        self.btn_remove.disable()
        self.inp_name.disable()
        self.btn_name.disable()
        self.inp_key.disable()
        self.btn_key.disable()

    def play(self, stack=False):
        #player = kplaystud.Clip(self.k, self.res, self.clip_id)
        #self.k.player.open(player, stack)
        ##p.reset()
        ## FIXME
        #player.hide()
        #player.show()
        #player.play()
        player = Player(self.k, self.clip_id, self.loop, self.jumps, selection_regions_json=self.selection_regions)
        if not player.go:
            return None
        self.k.player.open(player, stacked=stack)

        if self.k.music.active:
            self.k.job(self.k.music.cache_all_slots_for_player, args=(player.go,))

        self.k.player.play()
        return player

    def remove_clip(self):
        self.k.panel_project.panel_studio.panel_clip.remove_clip(self)

    def click(self, element, target=None):
        if element == self.btn_play:
            self.play()

        elif element == self.btn_name:
            kdb.set_clip_name(self.clip_id, self.inp_name.get_text())
            kdb.touch_clip(self.clip_id)

        elif element == self.btn_key:
            key = self.inp_key.get_text()
            key = ord(key) if key else None
            if key != self.key:
                if key and key in self.k.panel_project.panel_studio.keys:
                    # key is already used
                    self.inp_key.set_text(chr(self.key) if self.key else '')
                else:
                    kdb.set_clip_key(self.clip_id, key)
                    kdb.touch_clip(self.clip_id)
                    if self.key:
                        del self.k.panel_project.panel_studio.keys[self.key]
                    self.k.panel_project.panel_studio.keys[key] = self
                    self.key = key
        elif element == self.btn_remove:
            self.k.confirm(
                self.remove_clip,
                'Remove Clip from Project?',
                'Remove',
                'Are you sure you want to remove this clip?'
            )

    def keydown(self, key, mod):
        if key == self.key:
            stack = mod & pygame.KMOD_SHIFT
            self.play(stack)