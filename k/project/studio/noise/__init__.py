from k.ui import *
import k.project.studio.noise.library as nlib
import k.project.studio.noise.generator as ngen


class Panel(KPanel):
    def __init__(self, k, anchors, container):
        super().__init__(k, anchors, container)

        self.btn_library = pygame_gui.elements.UIButton(
            text='Library',
            manager=k.gui,
            container=self.container,
            relative_rect=SPACER)

        self.btn_generator = pygame_gui.elements.UIButton(
            text='Generator',
            manager=k.gui,
            container=self.container,
            anchors=target(self.btn_library),
            relative_rect=SPACER)

        self.panel_library = nlib.Panel(k,
            target(self.btn_library, 'top'), self.container)
        self.panel_library.hide()

        self.panel_generator = ngen.Panel(k,
            target(self.btn_generator, 'top'), self.container)
        self.panel_generator.hide()

        self.cur_btn = self.btn_library
        self.cur_btn.disable()
        self.cur_panel = self.panel_library

    def show(self):
        super().show()
        if self.cur_panel != self.panel_library:
            self.panel_library.hide()
        if self.cur_panel != self.panel_generator:
            self.panel_generator.hide()

    def click(self, element, target=None):
        if element == self.btn_library:
            self.panel_swap(self.btn_library, self.panel_library)

        elif element == self.btn_generator:
            self.panel_swap(self.btn_generator, self.panel_generator)

        else:
            self.cur_panel.click(element, target)

    def keydown(self, key, mod):
        self.cur_panel.keydown(key, mod)

    def keyup(self, key, mod):
        self.cur_panel.keyup(key, mod)

