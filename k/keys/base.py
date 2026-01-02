from k.ui import *
from abc import ABC, abstractmethod


KEY = (50, 50)
KEY_TOP = (KEY[0], KEY[1] - 20)
GAP_TOP = 15

INFO_TRY_MODS='NOTHING: This key does nothing on its own. Try using a modifier key (e.g. Shift, Ctrl) first.'

INFO_MOD='NOTHING: This is a modifier key and does nothing on its own. Try using it in combination with another key.'

INFO_NONE='NOTHING: Try changing order or combination.'


class Keys(KPanel, ABC):
    def __init__(self, panel, anchors, container):
        super().__init__(panel.k, anchors, container,
            relative_rect=pygame.Rect((0, 20), (WIDTH-PWIDTH-20, 300)))

        self.panel = panel
        self.keys = { }
        self.nops = { }
        self.cuts = { }
        self.info = { }
        self.pushed = [ ]

    def key(self, key, label, pos=(0, 0), size=KEY, left=None, top=None,
            info=None):
        self._add_(True, key, label, pos, size, left, top)
        if not info: info = INFO_TRY_MODS
        self.info[(key,)] = info.strip()

    def nop(self, key, label, pos=(0, 0), size=KEY, left=None, top=None):
        self._add_(False, key, label, pos, size, left, top)

    def cut(self, cut_id, pos=(0, 0), size=KEY, left=None, top=None):
        self._add_(None, cut_id, '...', pos, size, left, top)

    def _add_(self, used, key, label, pos, size, left, top):
        assert key not in self.keys and key not in self.nops \
            and key not in self.cuts, f'key/nop/cut already assigned: {key}'

        anchors = ANCHOR
        if left:
            elem = self.keys[left] if left in self.keys else \
                   self.nops[left] if left in self.nops else \
                   self.cuts[left]
            anchors = target(elem, 'left', anchors)
            if not top and 'top_target' in elem.anchors:
                anchors = target(elem.anchors['top_target'], 'top', anchors)
        if top:
            elem = self.keys[top] if top in self.keys else \
                   self.nops[top] if top in self.nops else \
                   self.cuts[top]
            anchors = target(elem, 'top', anchors)

        if isinstance(size, int):
            size = (KEY[0]+size, KEY[1])

        if used is True:
            self.keys[key] = pygame_gui.elements.UIButton(
                text=label,
                manager=self.k.gui,
                container=self.container,
                anchors=anchors,
                relative_rect=pygame.Rect(pos, size))

        elif used is False:
            self.nops[key] = pygame_gui.elements.UITextEntryLine(
                manager=self.k.gui,
                container=self.container,
                anchors=anchors,
                relative_rect=pygame.Rect(pos, size))
            self.nops[key].set_text(label)
            self.nops[key].disable()

        else:
            self.cuts[key] = pygame_gui.elements.UILabel(
                text=label,
                manager=self.k.gui,
                container=self.container,
                anchors=anchors,
                relative_rect=pygame.Rect(pos, size))

    def combo(self, keys, info):
        assert keys not in self.info, f'combo info already registered: {keys}'

        self.info[keys] = info

    def pushed_keys(self):
        if len(self.pushed) > 0:
            try: info = self.info[tuple(self.pushed)]
            except KeyError: info = INFO_NONE
            labels = [ self.keys[key].text for key in self.pushed ]
            self.panel.key_info(labels, info)

        else:
            self.reset()

    def reset(self):
        for button in self.keys.values():
            button.enable()

        self.pushed = [ ]
        self.panel.btn_reset.disable()
        self.panel.key_info(None, None)

    def hide(self):
        super().hide()
        self.reset()

    @abstractmethod
    def title(self):
        pass

    @abstractmethod
    def descr(self):
        pass

    def all(self):
        return (self.title(), self.descr(), [
            ([self.keys[key].text for key in keys],
                info if info != INFO_NONE \
                    and info != INFO_MOD and info != INFO_TRY_MODS else None) \
            for keys, info in self.info.items()
        ])

    def keydown(self, key):
        if key in self.keys and key not in self.pushed:
            self.panel.btn_reset.enable()
            self.pushed.append(key)
            self.keys[key].disable()
            self.pushed_keys()

    def keyup(self, key):
        if key in self.pushed:
            del self.pushed[self.pushed.index(key)]
            self.keys[key].enable()
            self.pushed_keys()

    def click(self, element, target=None):
        for key, button in self.keys.items():
            if element is button:
                if key not in self.pushed:
                    self.panel.btn_reset.enable()
                    self.pushed.append(key)
                button.disable()
                self.pushed_keys()
                return True

        return False

