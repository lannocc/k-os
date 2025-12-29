from k.ui import *
from .library import Panel as Library
from .studio import Panel as Studio
#import k.project.flip as pflip


class Panel(KPanel):
    def __init__(self, k, anchors):
        super().__init__(k, anchors)

        self.btn_library = pygame_gui.elements.UIButton(
            text='Library',
            manager=k.gui,
            container=self.container,
            relative_rect=SPACER)

        self.btn_studio = pygame_gui.elements.UIButton(
            text='Studio',
            manager=k.gui,
            container=self.container,
            anchors=target(self.btn_library),
            relative_rect=SPACER)

        #self.btn_flip = pygame_gui.elements.UIButton(
        #    text='Flip',
        #    manager=k.gui,
        #    container=self.container,
        #    anchors=target(self.btn_studio),
        #    relative_rect=SPACER)

        self.panel_library = Library(k,
            target(self.btn_library, 'top'), self.container)
        self.panel_library.hide()

        self.panel_studio = Studio(k,
            target(self.btn_studio, 'top'), self.container)
        self.panel_studio.hide()

        #self.panel_flip = pflip.Panel(k,
        #    target(self.btn_flip, 'top'), self.container)
        #self.panel_flip.hide()

        self.cur_btn = self.btn_library
        self.cur_btn.disable()
        self.cur_panel = self.panel_library

    def show(self):
        super().show()
        #if self.cur_panel != self.panel_library:
        #    self.panel_library.hide()
        #if self.cur_panel != self.panel_studio:
        #    self.panel_studio.hide()
        self.panel_library.hide()
        self.panel_studio.hide()
        self.panel_swap(self.cur_btn, self.cur_panel)
        #if self.cur_panel != self.panel_flip:
        #    self.panel_flip.hide()

    def panel_swap(self, btn, panel):
        #if self.cur_panel == self.panel_studio:
        #    self.panel_studio.suspend()

        super().panel_swap(btn, panel)

    def click(self, element, target=None):
        if element == self.btn_library:
            self.panel_swap(self.btn_library, self.panel_library)

        elif element == self.btn_studio:
            self.panel_swap(self.btn_studio, self.panel_studio)

        #elif element == self.btn_flip:
        #    self.panel_swap(self.btn_flip, self.panel_flip)

        else:
            self.cur_panel.click(element, target)

    def keydown(self, key, mod):
        self.cur_panel.keydown(key, mod)

    def keyup(self, key, mod):
        self.cur_panel.keyup(key, mod)

