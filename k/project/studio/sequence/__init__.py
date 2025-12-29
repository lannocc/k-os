from k.ui import *
from .library import Panel as Library
from .editor import Panel as Editor


class Panel(KPanel):
    def __init__(self, k, anchors, container):
        super().__init__(k, anchors, container)

        self.btn_library = pygame_gui.elements.UIButton(
            text='Library',
            manager=k.gui,
            container=self.container,
            relative_rect=SPACER)

        self.btn_editor = pygame_gui.elements.UIButton(
            text='Editor',
            manager=k.gui,
            container=self.container,
            anchors=target(self.btn_library),
            relative_rect=SPACER)

        self.panel_library = Library(k,
            target(self.btn_library, 'top'), self.container)
        self.panel_library.hide()

        self.panel_editor = Editor(k,
            target(self.btn_editor, 'top'), self.container)
        self.panel_editor.hide()

        self.cur_btn = self.btn_library
        self.cur_btn.disable()
        self.cur_panel = self.panel_library

    def show(self):
        super().show()
        self.panel_library.hide()
        self.panel_editor.hide()
        self.panel_swap(self.cur_btn, self.cur_panel)

    def close_project(self):
        self.panel_library.close_project()
        self.panel_editor.close_seq()

    def refresh_seqs(self):
        self.panel_library.refresh()

    def click(self, element, target=None):
        if element == self.btn_library:
            self.panel_swap(self.btn_library, self.panel_library)

        elif element == self.btn_editor:
            self.panel_swap(self.btn_editor, self.panel_editor)

        else:
            self.cur_panel.click(element, target)

