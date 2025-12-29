from k.ui import *
import k.db as kdb
import k.storage as media
from .clip import Panel as Clip
from .sequence import Panel as Seq
#import k.project.studio.noise as pnoise
#import k.project.studio.macro as pmacro

from datetime import datetime


NO_HSPACE = pygame.Rect((0, 10), (-1, -1))


class Panel(KPanel):
    def __init__(self, k, anchors, container):
        super().__init__(k, anchors, container)

        self.project_id = None

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
            relative_rect=pygame.Rect((10, 10), (380, -1)))

        self.btn_name = pygame_gui.elements.UIButton(
            text='Name',
            manager=k.gui,
            container=self.container,
            anchors=target(self.inp_name),
            relative_rect=SPACER)

        self.btn_clip = pygame_gui.elements.UIButton(
            text='Clip',
            manager=k.gui,
            container=self.container,
            anchors=target(self.btn_name, 'top'),
            relative_rect=SPACER)

        self.btn_seq = pygame_gui.elements.UIButton(
            text='Seq',
            manager=k.gui,
            container=self.container,
            anchors=target(self.btn_name, 'top', target(self.btn_clip)),
            relative_rect=NO_HSPACE)

        #self.btn_noise = pygame_gui.elements.UIButton(
        #    text='Noise',
        #    manager=k.gui,
        #    container=self.container,
        #    anchors=target(self.btn_name, 'top', target(self.btn_seq)),
        #    relative_rect=NO_HSPACE)

        #self.btn_macro = pygame_gui.elements.UIButton(
        #    text='Macro',
        #    manager=k.gui,
        #    container=self.container,
        #    anchors=target(self.btn_name, 'top', target(self.btn_noise)),
        #    relative_rect=NO_HSPACE)

        #self.lbl_sep = pygame_gui.elements.UILabel(
        #    text='|',
        #    manager=k.gui,
        #    container=self.container,
        #    anchors=target(self.btn_name, 'top', target(self.btn_macro)),
        #    relative_rect=pygame.Rect((10,15), (-1,-1)))

        #self.btn_open = pygame_gui.elements.UIButton(
        #    text='New',
        #    manager=k.gui,
        #    container=self.container,
        #    anchors=target(self.btn_name, 'top', target(self.lbl_sep)),
        #    relative_rect=SPACER)

        #self.btn_used = pygame_gui.elements.UIButton(
        #    text='Used',
        #    manager=k.gui,
        #    container=self.container,
        #    anchors=target(self.btn_name, 'top', target(self.btn_open)),
        #    relative_rect=NO_HSPACE)

        #self.btn_keys = pygame_gui.elements.UIButton(
        #    text='Keyed',
        #    manager=k.gui,
        #    container=self.container,
        #    anchors=target(self.btn_name, 'top', target(self.btn_used)),
        #    relative_rect=NO_HSPACE)

        self.panel_clip = Clip(k, target(self.btn_clip, 'top'), self.container)
        self.panel_clip.hide()

        self.panel_seq = Seq(k, target(self.btn_seq, 'top'), self.container)
        self.panel_seq.hide()

        #self.panel_noise = pnoise.Panel(k,
        #    target(self.btn_noise, 'top'), self.container)
        #self.panel_noise.hide()

        #self.panel_macro = pmacro.Panel(k,
        #    target(self.btn_macro, 'top'), self.container)
        #self.panel_macro.hide()

        self.cur_btn = self.btn_clip
        self.cur_btn.disable()
        self.cur_panel = self.panel_clip
        #self.cur_btn_mod = self.btn_keys
        #self.cur_btn_mod.disable()

        self.keys = {}
        self.started = None

    def show(self):
        super().show()
        #if self.cur_panel != self.panel_clip:
        #    self.panel_clip.hide()
        #if self.cur_panel != self.panel_seq:
        #    self.panel_seq.hide()
        self.panel_clip.hide()
        self.panel_seq.hide()
        self.panel_swap(self.cur_btn, self.cur_panel)
        #if self.cur_panel != self.panel_noise:
        #    self.panel_noise.hide()
        #if self.cur_panel != self.panel_macro:
        #    self.panel_macro.hide()

    def init_project(self):
        if self.project_id:
            kdb.touch_project(self.project_id)

        else:
            self.project_id = kdb.insert_project()
            media.start_project(self.project_id)
            self.panel_clip.refresh_clips()
            self.panel_seq.refresh_seqs()
            self.started = None

            self.k.panel_project.panel_library.refresh(self.project_id)
            self.btn_close.enable()

        return self.project_id

    def open_project(self, project_id):
        self.close_project()
        project = kdb.get_project(project_id)

        self.project_id = project_id
        self.btn_close.enable()

        name = project['name']
        if name:
            self.inp_name.set_text(name)

        self.panel_clip.refresh_clips()
        self.panel_seq.refresh_seqs()
        self.k.panel_project.panel_library.refresh(self.project_id)
        self.started = None

    def close_project(self):
        self.project_id = None
        self.btn_close.disable()
        self.inp_name.set_text('')

        self.panel_clip.close_project()
        self.panel_seq.close_project()

        self.keys = {}
        self.k.panel_project.panel_library.refresh()

    #def suspend(self):
    #    self.btn_close.enable()
    #    self.inp_name.enable()
    #    self.btn_name.enable()

    #    self.panel_clip.enable()
    #    self.k.player.suspend()
    #    self.started = None

    #def resume(self):
    #    self.btn_close.disable()
    #    self.inp_name.disable()
    #    self.btn_name.disable()

    #    self.panel_clip.disable()
    #    self.k.player.resume()
    #    self.started = datetime.now()

    def panel_swap(self, btn, panel):
        '''
        if self.cur_panel == self.panel_flip:
            #if self.cur_btn_mod != self.btn_keys:
            #    self.btn_keys.enable()
            #if self.cur_btn_mod != self.btn_open:
            #    self.btn_open.enable()
            #if self.cur_btn_mod != self.btn_used:
            #    self.btn_used.enable()
            self.lbl_sep.show()
            self.btn_keys.show()
            self.btn_open.show()
            self.btn_used.show()
        '''

        super().panel_swap(btn, panel)

        '''
        if panel == self.panel_flip:
            #self.btn_keys.disable()
            #self.btn_open.disable()
            #self.btn_used.disable()
            self.lbl_sep.hide()
            self.btn_keys.hide()
            self.btn_open.hide()
            self.btn_used.hide()
        '''

    #def panel_mod(self, btn):
    #    self.cur_btn_mod.enable()
    #    self.cur_btn_mod = btn
    #    self.cur_btn_mod.disable()

    def click(self, element, target=None):
        if element == self.btn_close:
            self.close_project()

        elif element == self.btn_name:
            self.init_project()
            kdb.set_project_name(self.project_id, self.inp_name.get_text())
            self.k.panel_project.panel_library.refresh(self.project_id)

        elif element == self.btn_clip:
            self.panel_swap(self.btn_clip, self.panel_clip)

        elif element == self.btn_seq:
            self.panel_swap(self.btn_seq, self.panel_seq)

        #elif element == self.btn_noise:
        #    self.panel_swap(self.btn_noise, self.panel_noise)

        #elif element == self.btn_macro:
        #    self.panel_swap(self.btn_macro, self.panel_macro)

        #elif element == self.btn_keys:
        #    self.panel_mod(self.btn_keys)

        #elif element == self.btn_open:
        #    self.panel_mod(self.btn_open)

        #elif element == self.btn_used:
        #    self.panel_mod(self.btn_used)

        else:
            self.cur_panel.click(element, target)

    def keydown(self, key, mod):
        if key == pygame.K_BREAK:
            #if self.started:
            #    self.suspend()
            #else:
            #    self.resume()
            pass

        else:
            if self.started:
                #for entry in self.clips:
                #    entry.keydown(key, mod)
                if key in self.keys:
                    self.keys[key].keydown(key, mod)

            self.cur_panel.keydown(key, mod)

    def keyup(self, key, mod):
        if key == pygame.K_BREAK:
            pass

        else:
            self.cur_panel.keyup(key, mod)

