from .base import *


def seek(count):
    txt = 'Jump '
    if count == 1: txt += 'to next frame.'
    elif count == -1: txt += 'to previous frame.'
    else:
        txt += f'{abs(count)} frames '
        txt += 'forward.' if count > 0 else 'backward.'
    return txt


class Panel(Keys):
    def __init__(self, panel, anchors, container):
        super().__init__(panel, anchors, container)

        self.key(pygame.K_ESCAPE, 'Esc', size=KEY_TOP,
            info='BIG: Return to normal size.\n' \
               + 'NORMAL: Close player.')
        self.cut('c0', size=(KEY[0]+40, KEY_TOP[1]), left=pygame.K_ESCAPE)
        self.nop(pygame.K_PRINT, 'PS', size=KEY_TOP, left='c0')
        self.key(pygame.K_SCROLLOCK, 'Scr', size=KEY_TOP, left=pygame.K_PRINT,
            info='Toggle player size.')
        self.nop(pygame.K_BREAK, 'Brk', size=KEY_TOP, left=pygame.K_SCROLLOCK)

        self.nop(pygame.K_BACKQUOTE, '`', (0, GAP_TOP), top=pygame.K_ESCAPE)
        self.cut('c1', (0, GAP_TOP), size=40, left=pygame.K_BACKQUOTE)
        self.nop(pygame.K_INSERT, 'Ins', (0, GAP_TOP), left='c1')
        self.key(pygame.K_HOME, 'Hom', (0, GAP_TOP), left=pygame.K_INSERT,
            info='Restart playback from beginning.')
        self.nop(pygame.K_PAGEUP, 'PUp', (0, GAP_TOP), left=pygame.K_HOME)
        self.nop(pygame.K_NUMLOCK, 'Num', (KEY[0]//2, GAP_TOP),
            left=pygame.K_PAGEUP)
        self.key(pygame.K_KP_DIVIDE, '/', (0, GAP_TOP), left=pygame.K_NUMLOCK,
            info='Set start of loop to the current frame.')
        self.key(pygame.K_KP_MULTIPLY, '*', (0, GAP_TOP),
            left=pygame.K_KP_DIVIDE,
            info='Set end of loop to the current frame.')
        self.key(pygame.K_KP_MINUS, '-', (0, GAP_TOP),
            left=pygame.K_KP_MULTIPLY,
            info='Disable loop / go to loop end.')

        self.nop(pygame.K_TAB, 'Tab', size=KEY[0]//2, top=pygame.K_BACKQUOTE)
        self.cut('c2', size=15, left=pygame.K_TAB)
        self.key(pygame.K_DELETE, 'Del', left='c2',
            info='Close player.')
        self.key(pygame.K_END, 'End', left=pygame.K_DELETE,
            info='Stop playback.')
        self.nop(pygame.K_PAGEDOWN, 'PDn', left=pygame.K_END)
        self.key(pygame.K_KP7, '7', (KEY[0]//2, 0), left=pygame.K_PAGEDOWN,
            info='Jump to position #7.')
        self.combo((pygame.K_LCTRL, pygame.K_KP7),
            info='Set jump position #7 to the current frame.')
        self.key(pygame.K_KP8, '8', left=pygame.K_KP7,
            info='Jump to position #8.')
        self.combo((pygame.K_LCTRL, pygame.K_KP8),
            info='Set jump position #8 to the current frame.')
        self.key(pygame.K_KP9, '9', left=pygame.K_KP8,
            info='Jump to position #9.')
        self.combo((pygame.K_LCTRL, pygame.K_KP9),
            info='Set jump position #9 to the current frame.')
        self.key(pygame.K_KP_PLUS, '+', size=(KEY[0], KEY[1]*2),
            left=pygame.K_KP9,
            info='Enable loop / go to loop beginning.')

        self.nop(pygame.K_CAPSLOCK, 'CapsLock', size=KEY[0]//2+15,
            top=pygame.K_TAB)
        self.cut('c3', left=pygame.K_CAPSLOCK)
        self.key(pygame.K_KP4, '4', (KEY[0]*3+KEY[0]//2, 0), left='c3',
            info='Jump to position #4.')
        self.combo((pygame.K_LCTRL, pygame.K_KP4),
            info='Set jump position #4 to the current frame.')
        self.key(pygame.K_KP5, '5', left=pygame.K_KP4,
            info='Jump to position #5.')
        self.combo((pygame.K_LCTRL, pygame.K_KP5),
            info='Set jump position #5 to the current frame.')
        self.key(pygame.K_KP6, '6', left=pygame.K_KP5,
            info='Jump to position #6.')
        self.combo((pygame.K_LCTRL, pygame.K_KP6),
            info='Set jump position #6 to the current frame.')

        self.key(pygame.K_LSHIFT, 'Shift', size=KEY[0]+15,
            top=pygame.K_CAPSLOCK, info=INFO_MOD)
        self.cut('c4', size=25, left=pygame.K_LSHIFT)
        self.key(pygame.K_UP, 'Up', left='c4',
            info=f'PLAYING: {seek(PLAY_SEEK_VERT)}\n' \
               + f'PAUSED: {seek(PAUSE_SEEK_VERT)}')
        self.combo((pygame.K_LCTRL, pygame.K_UP),
            info=f'PLAYING: {seek(PLAY_SEEK_VERT_CTRL)}\n' \
               + f'PAUSED: {seek(PAUSE_SEEK_VERT_CTRL)}')
        self.combo((pygame.K_LSHIFT, pygame.K_UP),
            info=f'PLAYING: {seek(PLAY_SEEK_VERT_SHIFT)}\n' \
               + f'PAUSED: {seek(PAUSE_SEEK_VERT_SHIFT)}')
        self.key(pygame.K_KP1, '1', (KEY[0]+KEY[0]//2, 0), left=pygame.K_UP,
            info='Jump to position #1.')
        self.combo((pygame.K_LCTRL, pygame.K_KP1),
            info='Set jump position #1 to the current frame.')
        self.key(pygame.K_KP2, '2', left=pygame.K_KP1,
            info='Jump to position #2.')
        self.combo((pygame.K_LCTRL, pygame.K_KP2),
            info='Set jump position #2 to the current frame.')
        self.key(pygame.K_KP3, '3', left=pygame.K_KP2,
            info='Jump to position #3.')
        self.combo((pygame.K_LCTRL, pygame.K_KP3),
            info='Set jump position #3 to the current frame.')
        self.key(pygame.K_KP_ENTER, 'Ent', size=(KEY[0], KEY[1]*2),
            left=pygame.K_KP3,
            info='Pause / resume playback.')

        self.key(pygame.K_LCTRL, 'Ctrl', size=KEY[0]//2, top=pygame.K_LSHIFT,
            info=INFO_MOD)
        self.cut('c5', size=15, left=pygame.K_LCTRL)
        self.key(pygame.K_LEFT, '<--', left='c5',
            info=seek(-SEEK_HORIZ))
        self.combo((pygame.K_LCTRL, pygame.K_LEFT),
            info=seek(-SEEK_HORIZ_CTRL))
        self.combo((pygame.K_LSHIFT, pygame.K_LEFT),
            info=seek(-SEEK_HORIZ_SHIFT))
        self.key(pygame.K_DOWN, 'Dn', left=pygame.K_LEFT,
            info=f'PLAYING: {seek(-PLAY_SEEK_VERT)}\n' \
               + f'PAUSED: {seek(-PAUSE_SEEK_VERT)}')
        self.combo((pygame.K_LCTRL, pygame.K_DOWN),
            info=f'PLAYING: {seek(-PLAY_SEEK_VERT_CTRL)}\n' \
               + f'PAUSED: {seek(-PAUSE_SEEK_VERT_CTRL)}')
        self.combo((pygame.K_LSHIFT, pygame.K_DOWN),
            info=f'PLAYING: {seek(-PLAY_SEEK_VERT_SHIFT)}\n' \
               + f'PAUSED: {seek(-PAUSE_SEEK_VERT_SHIFT)}')
        self.key(pygame.K_RIGHT, '-->', left=pygame.K_DOWN,
            info=seek(SEEK_HORIZ))
        self.combo((pygame.K_LCTRL, pygame.K_RIGHT),
            info=seek(SEEK_HORIZ_CTRL))
        self.combo((pygame.K_LSHIFT, pygame.K_RIGHT),
            info=seek(SEEK_HORIZ_SHIFT))
        self.key(pygame.K_KP0, '0', (KEY[0]//2, 0), size=KEY[0],
            left=pygame.K_RIGHT,
            info='Jump to beginning.')
        self.key(pygame.K_KP_PERIOD, '.', left=pygame.K_KP0,
            info='Hold.')

    def title(self):
        return 'PLAYER'

    def descr(self):
        return 'When the player is open, the following key shortcuts become ' \
             + 'available. The keyboard numpad area must be used for ' \
             + 'numbered items. When music mode is active (toggled with ' \
             + 'Ctrl+M), F1-F12 keys can be used for live audio looping ' \
             + '(short press to toggle, long press to record).'

