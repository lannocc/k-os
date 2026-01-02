from k.ui import *
from .library import Panel as Library
from .youtube import Panel as YouTube


class Panel(KPanel):
    def __init__(self, k, anchors):
        super().__init__(k, anchors)

        self.btn_library = pygame_gui.elements.UIButton(
            text='Library',
            manager=k.gui,
            container=self.container,
            relative_rect=SPACER)

        self.btn_youtube = pygame_gui.elements.UIButton(
            text='YouTube',
            manager=k.gui,
            container=self.container,
            anchors=target(self.btn_library),
            relative_rect=SPACER)

        self.panel_library = Library(k,
            target(self.btn_library, 'top'), self.container)
        self.panel_library.hide()

        self.panel_youtube = YouTube(k,
            target(self.btn_youtube, 'top'), self.container)
        self.panel_youtube.hide()

        self.cur_btn = self.btn_library
        self.cur_btn.disable()
        self.cur_panel = self.panel_library
        #self.cur_panel.show()

    def show(self):
        super().show()
        if self.cur_panel != self.panel_library:
            self.panel_library.hide()
        if self.cur_panel != self.panel_youtube:
            self.panel_youtube.hide()

    def click(self, element, target=None):
        if element == self.btn_library:
            self.panel_swap(self.btn_library, self.panel_library)

        elif element == self.btn_youtube:
            self.panel_swap(self.btn_youtube, self.panel_youtube)

        else:
            self.cur_panel.click(element, target)

