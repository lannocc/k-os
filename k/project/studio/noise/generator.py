from k.ui import *

import numpy
import pygame.sndarray


def sineWave(freq):
    return pygame.sndarray.make_sound(numpy.array([8192 * numpy.sin(2.0 * numpy.pi * freq * x / SAMPLE_RATE) for x in range(0, SAMPLE_RATE)]).astype(numpy.int16))


class Panel(KPanel):
    def __init__(self, k, anchors, container):
        super().__init__(k, anchors, container)

        self.sounds = None

        self.status = pygame_gui.elements.UIButton(
            #text='Preparing sounds, PLEASE WAIT...',
            text='Click to Start',
            manager=k.gui,
            container=self.container,
            relative_rect=SPACER)

    def click(self, element, target=None):
        if element == self.status:
            if self.sounds:
                self.sounds = None
                self.status.set_text('Click to Start')
            else:
                self.status.set_text('Preparing sounds...')
                self.status.disable()
                self.k.job(self.start)

    def start(self):
        sounds = { }
        sounds[pygame.K_LSHIFT] = sineWave(220)
        sounds[pygame.K_z] = sineWave(233.08)
        sounds[pygame.K_x] = sineWave(246.94)
        sounds[pygame.K_c] = sineWave(261.63)
        sounds[pygame.K_v] = sineWave(277.18)
        sounds[pygame.K_b] = sineWave(293.66)
        sounds[pygame.K_n] = sineWave(311.13)
        sounds[pygame.K_m] = sineWave(329.63)
        sounds[pygame.K_COMMA] = sineWave(349.23)
        sounds[pygame.K_PERIOD] = sineWave(369.99)
        sounds[pygame.K_SLASH] = sineWave(392)
        sounds[pygame.K_RSHIFT] = sineWave(415.30)
        sounds[pygame.K_CAPSLOCK] = sineWave(440)
        sounds[pygame.K_a] = sineWave(466.16)
        sounds[pygame.K_s] = sineWave(493.88)
        sounds[pygame.K_d] = sineWave(523.25)
        sounds[pygame.K_f] = sineWave(554.37)
        sounds[pygame.K_g] = sineWave(587.33)
        sounds[pygame.K_h] = sineWave(622.25)
        sounds[pygame.K_j] = sineWave(659.25)
        sounds[pygame.K_k] = sineWave(698.46)
        sounds[pygame.K_l] = sineWave(739.99)
        sounds[pygame.K_SEMICOLON] = sineWave(783.99)
        sounds[pygame.K_QUOTE] = sineWave(830.61)
        sounds[pygame.K_TAB] = sineWave(880)
        sounds[pygame.K_q] = sineWave(932.22)
        sounds[pygame.K_w] = sineWave(987.77)
        sounds[pygame.K_e] = sineWave(1046.50)
        sounds[pygame.K_r] = sineWave(1108.73)
        sounds[pygame.K_t] = sineWave(1174.66)
        sounds[pygame.K_y] = sineWave(1244.51)
        sounds[pygame.K_u] = sineWave(1318.51)
        sounds[pygame.K_i] = sineWave(1396.91)
        sounds[pygame.K_o] = sineWave(1479.98)
        sounds[pygame.K_p] = sineWave(1567.98)
        sounds[pygame.K_LEFTBRACKET] = sineWave(1661.22)
        sounds[pygame.K_BACKQUOTE] = sineWave(1760)
        sounds[pygame.K_1] = sineWave(1864.66)
        sounds[pygame.K_2] = sineWave(1975.53)
        sounds[pygame.K_3] = sineWave(2093)
        sounds[pygame.K_4] = sineWave(2217.46)
        sounds[pygame.K_5] = sineWave(2349.32)
        sounds[pygame.K_6] = sineWave(2489.02)
        sounds[pygame.K_7] = sineWave(2637.02)
        sounds[pygame.K_8] = sineWave(2793.83)
        sounds[pygame.K_9] = sineWave(2959.96)
        sounds[pygame.K_0] = sineWave(3135.96)
        sounds[pygame.K_MINUS] = sineWave(3322.44)
        sounds[pygame.K_EQUALS] = sineWave(3520)
        self.sounds = sounds

        self.status.set_text('Press key(s) for sound')
        self.status.enable()

    def keydown(self, key, mod):
        print('down')
        print(key)

        if self.sounds:
            if key in self.sounds:
                self.sounds[key].play(-1)

    def keyup(self, key, mod):
        print('up')
        print(key)

        if self.sounds:
            if key in self.sounds:
                self.sounds[key].stop()

