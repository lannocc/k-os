from k.ui import *
import k.meta
from k.meta.shadow import SW, SH

import pygame.camera


class Mod(k.meta.Mod):
    def __init__(self, meta):
        if meta.fullscreen:
            super().__init__(meta, meta.kx + WIDTH, 0, meta.kx, meta.ky)
        else:
            super().__init__(meta, meta.kx + WIDTH - PWIDTH - SW,
                meta.ky + PHEIGHT, SW, SH)

        pygame.camera.init()
        self.cams = pygame.camera.list_cameras()
        self.log(f'webcams: {self.cams}')

        if self.cams:
            self.cam = pygame.camera.Camera(self.cams[0], (self.w, self.h))
            #self.img = pygame.Surface((self.w, self.h))
            self.img = None
        else:
            self.log(Exception('NO WEBCAM'))
            self.cam = None
            self.img = self.meta.font3.render('NO WEBCAM', True, RED)

            self.meta.screen.blit(self.img, ((self.x + 5,
                self.y + self.h - self.img.get_height() - 5)))

    def init(self):
        if self.cam:
            self.cam.start()
            self.img = self.cam.get_image()

            w = self.img.get_width()
            h = self.img.get_height()

            if w > self.w or h > self.h:
                sw = w
                sh = h

                if w > self.w:
                    scale = self.w / w
                    sw = self.w
                    sh = int(scale * h)

                if sh > self.h:
                    scale = self.h / h
                    sw = int(scale * w)
                    sh = self.h

                if sw < self.w and not self.meta.fullscreen:
                    self.x += self.w - sw
                self.w = sw
                if sh < self.h and self.meta.fullscreen:
                    self.y += self.h - sh
                self.h = sh

                self.scaled = pygame.transform.scale(self.img, (sw, sh))

            else:
                self.scaled = self.img

    def tick(self):
        if not self.cam \
                or (not self.meta.fullscreen and not self.meta.metamode) \
                or not self.cam.query_image():
            return

        self.cam.get_image(self.img)
        self.mirror = pygame.transform.flip(self.img, True, False)

        if self.focused:
            if self.meta.fullscreen:
                self.meta.screen.blit(self.img,
                    (self.meta.size[0] - self.img.get_width(), 0))
            else:
                self.meta.screen.blit(self.mirror,
                    (self.meta.kx + WIDTH - PWIDTH - self.mirror.get_width(),
                    self.y))

        else:
            if self.scaled != self.img:
                pygame.transform.scale(self.mirror,
                    (self.w, self.h), self.scaled)

            self.meta.screen.blit(self.scaled, ((self.x, self.y)))

        #if self.meta.fullscreen and self.meta.metamode \
        #        and not self.meta.k.player.big:
        #    if not self.meta.gaming and not self.meta.anyfocus:
        #        self.meta.screen.blit(self.img,
        #            (self.meta.kx + WIDTH - PWIDTH - self.img.get_width(),
        #            self.meta.ky + PHEIGHT))

    def unfocus(self):
        super().unfocus()
        self.meta.screen.fill(BLACK, pygame.Rect(
            (self.meta.size[0] - self.img.get_width(), 0),
            (self.img.get_width(), self.img.get_height())))

    def kill(self):
        if self.cam:
            self.cam.stop()

