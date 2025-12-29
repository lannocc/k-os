from .base import *


class Panel(Keys):
    def __init__(self, panel, anchors, container):
        super().__init__(panel, anchors, container)

        self.key(pygame.K_ESCAPE, 'Esc', size=KEY_TOP,
            info='Close the blackboard.')
        self.nop(pygame.K_F1, 'F1', (KEY[0], 0), KEY_TOP, left=pygame.K_ESCAPE)
        self.nop(pygame.K_F2, 'F2', size=KEY_TOP, left=pygame.K_F1)
        self.nop(pygame.K_F3, 'F3', size=KEY_TOP, left=pygame.K_F2)
        self.nop(pygame.K_F4, 'F4', size=KEY_TOP, left=pygame.K_F3)
        self.nop(pygame.K_F5, 'F5', (KEY[0]//2, 0), KEY_TOP, left=pygame.K_F4)
        self.nop(pygame.K_F6, 'F6', size=KEY_TOP, left=pygame.K_F5)
        self.nop(pygame.K_F7, 'F7', size=KEY_TOP, left=pygame.K_F6)

        self.key(pygame.K_BACKQUOTE, '`', (0, GAP_TOP), top=pygame.K_ESCAPE,
            info='Use the Color tool (toggle palette).')
        self.combo((pygame.K_LSHIFT, pygame.K_BACKQUOTE),
            info='Select color from canvas.')
        self.key(pygame.K_1, '1', (0, GAP_TOP), left=pygame.K_BACKQUOTE,
            info='Choose color #1.')
        self.key(pygame.K_2, '2', (0, GAP_TOP), left=pygame.K_1,
            info='Choose color #2.')
        self.key(pygame.K_3, '3', (0, GAP_TOP), left=pygame.K_2,
            info='Choose color #3.')
        self.key(pygame.K_4, '4', (0, GAP_TOP), left=pygame.K_3,
            info='Choose color #4.')
        self.key(pygame.K_5, '5', (0, GAP_TOP), left=pygame.K_4,
            info='Choose color #5.')
        self.key(pygame.K_6, '6', (0, GAP_TOP), left=pygame.K_5,
            info='Choose color #6.')
        self.key(pygame.K_7, '7', (0, GAP_TOP), left=pygame.K_6,
            info='Choose color #7.')
        self.key(pygame.K_8, '8', (0, GAP_TOP), left=pygame.K_7,
            info='Choose color #8.')
        self.key(pygame.K_9, '9', (0, GAP_TOP), left=pygame.K_8,
            info='Choose color #9.')

        self.nop(pygame.K_TAB, 'Tab', size=KEY[0]//2, top=pygame.K_BACKQUOTE)
        self.key(pygame.K_q, 'Q', left=pygame.K_TAB,
            info='Use the Queue-Query tool.')
        self.key(pygame.K_w, 'W', left=pygame.K_q,
            info='Use the Wiggle tool.')
        self.combo((pygame.K_LSHIFT, pygame.K_w),
            info='Select as Wiggle tool.')
        self.combo((pygame.K_LCTRL, pygame.K_w),
            info='Wiggle tool straight line.')
        self.key(pygame.K_e, 'E', left=pygame.K_w,
            info='Use the Ellipse tool.')
        self.combo((pygame.K_LSHIFT, pygame.K_e),
            info='Select as Ellipse tool.')
        self.combo((pygame.K_LCTRL, pygame.K_e),
            info='Ellipse tool perfect circle.')
        self.key(pygame.K_r, 'R', left=pygame.K_e,
            info='Use the Rectangle tool.')
        self.combo((pygame.K_LSHIFT, pygame.K_r),
            info='Select as Rectangle tool.')
        self.combo((pygame.K_LCTRL, pygame.K_r),
            info='Rectangle tool perfect square.')
        self.key(pygame.K_t, 'T', left=pygame.K_r,
            info='Use the Text tool.')
        self.combo((pygame.K_LSHIFT, pygame.K_t),
            info='Select as Text tool.')
        self.nop(pygame.K_y, 'Y', left=pygame.K_t)
        self.nop(pygame.K_u, 'U', left=pygame.K_y)
        self.nop(pygame.K_i, 'I', left=pygame.K_u)

        self.nop(pygame.K_CAPSLOCK, 'CapsLock', size=KEY[0]//2+15,
            top=pygame.K_TAB)
        self.key(pygame.K_a, 'A', left=pygame.K_CAPSLOCK,
            info='Use the Adjuster tool.')
        self.key(pygame.K_s, 'S', left=pygame.K_a,
            info='Save drawing.')
        self.key(pygame.K_d, 'D', left=pygame.K_s,
            info='Delete object.')
        self.key(pygame.K_f, 'F', left=pygame.K_d,
            info='Use the Fill tool.')
        self.key(pygame.K_g, 'G', left=pygame.K_f,
            info='Group.')
        self.nop(pygame.K_h, 'H', left=pygame.K_g)
        self.nop(pygame.K_j, 'J', left=pygame.K_h)
        self.nop(pygame.K_k, 'K', left=pygame.K_j)

        self.key(pygame.K_LSHIFT, 'Shift', size=KEY[0]+15,
            top=pygame.K_CAPSLOCK,
            info='Selection mode [in combination with tool use] '+INFO_MOD)
        self.key(pygame.K_z, 'Z', left=pygame.K_LSHIFT,
            info='Undo.')
        self.combo((pygame.K_LSHIFT, pygame.K_z),
            info='Redo.')
        self.combo((pygame.K_LCTRL, pygame.K_z),
            info='Redo all.')
        self.key(pygame.K_x, 'X', left=pygame.K_z,
            info='Cut.')
        self.key(pygame.K_c, 'C', left=pygame.K_x,
            info='Copy object to clipboard.')
        self.key(pygame.K_v, 'V', left=pygame.K_c,
            info='Paste clipboard contents as new object.')
        self.key(pygame.K_b, 'B', left=pygame.K_v,
            info='Background toggle.')
        self.nop(pygame.K_n, 'N', left=pygame.K_b)
        self.nop(pygame.K_m, 'M', left=pygame.K_n)

        self.key(pygame.K_LCTRL, 'Ctrl', size=KEY[0]//2, top=pygame.K_LSHIFT,
            info='Constraint mode [in combination with tool use] '+INFO_MOD)
        self.nop(pygame.K_LSUPER, 'Win', size=15, left=pygame.K_LCTRL)
        self.nop(pygame.K_LALT, 'Alt', size=15, left=pygame.K_LSUPER)
        self.key(pygame.K_SPACE, 'Space', size=KEY[0]*5, left=pygame.K_LALT,
            info='Toggle selectors.')

    def title(self):
        return 'ACK'

    def descr(self):
        return 'These keys apply when "ack" (blackboard) is active.'

