from k.ui import *
import k.game.library as glib
import k.game.studio as gstud
import k.game.gym as gym


class Panel(KPanel):
    def __init__(self, k, anchors):
        super().__init__(k, anchors)

        self.btn_library = pygame_gui.elements.UIButton(
            text='Library',
            manager=k.gui,
            container=self.container,
            relative_rect=SPACER)

        self.btn_studio = pygame_gui.elements.UIButton(
            text='Map / Stack',
            manager=k.gui,
            container=self.container,
            anchors=target(self.btn_library),
            relative_rect=SPACER)

        self.btn_gym = pygame_gui.elements.UIButton(
            text='Test',
            manager=k.gui,
            container=self.container,
            anchors=target(self.btn_studio),
            relative_rect=SPACER)

        self.panel_library = glib.Panel(k,
            target(self.btn_library, 'top'), self.container)
        self.panel_library.hide()

        self.panel_studio = gstud.Panel(k,
            target(self.btn_studio, 'top'), self.container)
        self.panel_studio.hide()

        self.panel_gym = gym.Panel(k,
            target(self.btn_gym, 'top'), self.container)
        self.panel_gym.hide()

        self.cur_btn = self.btn_library
        self.cur_btn.disable()
        self.cur_panel = self.panel_library

    def click(self, element, target=None):
        if element == self.btn_library:
            self.panel_swap(self.btn_library, self.panel_library)
        elif element == self.btn_studio:
            self.panel_swap(self.btn_studio, self.panel_studio)
        elif element == self.btn_gym:
            self.panel_swap(self.btn_gym, self.panel_gym)

