from .base import *


class Panel(Keys):
    def __init__(self, panel, anchors, container):
        super().__init__(panel, anchors, container)

        self.key(pygame.K_ESCAPE, 'Esc', size=KEY_TOP,
            info='Quit the application.')
        self.nop(pygame.K_F1, 'F1', (KEY[0], 0), KEY_TOP, left=pygame.K_ESCAPE)
        self.nop(pygame.K_F2, 'F2', size=KEY_TOP, left=pygame.K_F1)
        self.nop(pygame.K_F3, 'F3', size=KEY_TOP, left=pygame.K_F2)
        self.nop(pygame.K_F4, 'F4', size=KEY_TOP, left=pygame.K_F3)
        self.nop(pygame.K_F5, 'F5', (KEY[0]//2, 0), KEY_TOP, left=pygame.K_F4)
        self.nop(pygame.K_F6, 'F6', size=KEY_TOP, left=pygame.K_F5)
        self.nop(pygame.K_F7, 'F7', size=KEY_TOP, left=pygame.K_F6)

        self.nop(pygame.K_BACKQUOTE, '`', (0, GAP_TOP), top=pygame.K_ESCAPE)
        self.nop(pygame.K_1, '1', (0, GAP_TOP), left=pygame.K_BACKQUOTE)
        self.nop(pygame.K_2, '2', (0, GAP_TOP), left=pygame.K_1)
        self.nop(pygame.K_3, '3', (0, GAP_TOP), left=pygame.K_2)
        self.nop(pygame.K_4, '4', (0, GAP_TOP), left=pygame.K_3)
        self.nop(pygame.K_5, '5', (0, GAP_TOP), left=pygame.K_4)
        self.nop(pygame.K_6, '6', (0, GAP_TOP), left=pygame.K_5)
        self.nop(pygame.K_7, '7', (0, GAP_TOP), left=pygame.K_6)
        self.nop(pygame.K_8, '8', (0, GAP_TOP), left=pygame.K_7)
        self.nop(pygame.K_9, '9', (0, GAP_TOP), left=pygame.K_8)

        self.key(pygame.K_TAB, 'Tab', size=KEY[0]//2, top=pygame.K_BACKQUOTE,
            info='Toggle meta-mode (if not disabled on command line).')
        self.combo((pygame.K_LSHIFT, pygame.K_TAB),
            info='Show the "score" (performance metrics) in the terminal.')
        self.nop(pygame.K_q, 'Q', left=pygame.K_TAB)
        self.nop(pygame.K_w, 'W', left=pygame.K_q)
        self.nop(pygame.K_e, 'E', left=pygame.K_w)
        self.nop(pygame.K_r, 'R', left=pygame.K_e)
        self.nop(pygame.K_t, 'T', left=pygame.K_r)
        self.nop(pygame.K_y, 'Y', left=pygame.K_t)
        self.nop(pygame.K_u, 'U', left=pygame.K_y)
        self.nop(pygame.K_i, 'I', left=pygame.K_u)

        self.nop(pygame.K_CAPSLOCK, 'CapsLock', size=KEY[0]//2+15,
            top=pygame.K_TAB)
        self.key(pygame.K_a, 'A', left=pygame.K_CAPSLOCK)
        self.combo((pygame.K_LCTRL, pygame.K_a),
            info='Select all text (when cursor is in a text field).')
        self.nop(pygame.K_s, 'S', left=pygame.K_a)
        self.nop(pygame.K_d, 'D', left=pygame.K_s)
        self.nop(pygame.K_f, 'F', left=pygame.K_d)
        self.nop(pygame.K_g, 'G', left=pygame.K_f)
        self.nop(pygame.K_h, 'H', left=pygame.K_g)
        self.nop(pygame.K_j, 'J', left=pygame.K_h)
        self.nop(pygame.K_k, 'K', left=pygame.K_j)

        self.key(pygame.K_LSHIFT, 'Shift', size=KEY[0]+15,
            top=pygame.K_CAPSLOCK, info=INFO_MOD)
        self.nop(pygame.K_z, 'Z', left=pygame.K_LSHIFT)
        self.key(pygame.K_x, 'X', left=pygame.K_z)
        self.combo((pygame.K_LCTRL, pygame.K_x),
            info='Cut selected text (when cursor is in a text field).')
        self.key(pygame.K_c, 'C', left=pygame.K_x)
        self.combo((pygame.K_LCTRL, pygame.K_c),
            info='Copy selected text to clipboard (when cursor is in a text ' \
               + 'field).')
        self.key(pygame.K_v, 'V', left=pygame.K_c)
        self.combo((pygame.K_LCTRL, pygame.K_v),
            info='Paste clipboard contents (when cursor is in a text field).')
        self.nop(pygame.K_b, 'B', left=pygame.K_v)
        self.nop(pygame.K_n, 'N', left=pygame.K_b)
        self.nop(pygame.K_m, 'M', left=pygame.K_n)

        self.key(pygame.K_LCTRL, 'Ctrl', size=KEY[0]//2, top=pygame.K_LSHIFT,
            info=INFO_MOD)
        self.nop(pygame.K_LSUPER, 'Win', size=15, left=pygame.K_LCTRL)
        self.nop(pygame.K_LALT, 'Alt', size=15, left=pygame.K_LSUPER)
        self.nop(pygame.K_SPACE, 'Space', size=KEY[0]*5, left=pygame.K_LALT)

    def title(self):
        return 'GENERAL'

    def descr(self):
        return 'These apply throughout the GUI.'

