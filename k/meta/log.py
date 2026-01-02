from k.ui import *
import k.meta
from k.meta.shadow import SW, SH


PRIMER = (0, 0, 27)
OUTPUT = BLUE
OFOCUS = (128, 128, 255)
EXCEPT = RED
EFOCUS = (255, 128, 128)
TREEBG = (9, 81, 18)
TREEFG = (0, 222, 81)
TREESG = (181, 255, 242)


class Mod(k.meta.Mod):
    def __init__(self, meta):
        if meta.fullscreen:
            super().__init__(meta,
                0*meta.size[0]/3 + 5, meta.ky + HEIGHT + 5,
                meta.size[0]/3 - 10, meta.ky - 10)
        else:
            super().__init__(meta,
                0*meta.size[0]/3 + 5, meta.ky + PHEIGHT + SH + 5,
                meta.size[0]/3 - 10, HEIGHT - STATUS - PHEIGHT - SH - 10)

    def init(self):
        self.paint_primer()

        self.renders = []
        self.next = 0
        self.paint_history()

        self.tree = -1
        self.scroll = []
        self.img_info = None
        self.render_tree()
        self.paint_tree()

    def tick(self):
        if self.next >= len(self.log.hits):
            return

        for hit in self.log.hits[self.next:]:
            self.renders.append(
                (self.meta.font2.render(hit[1], True, OUTPUT),
                self.meta.font2.render(hit[1], True, OFOCUS)))

            if len(hit) > 2:
                for data in hit[2:]:    
                    if isinstance(data, Exception):
                        self.renders.append(
                            (self.meta.font1.render(f'{data}   ', True, EXCEPT),
                            self.meta.font1.render(f'{data}   ', True, EFOCUS)))
                    else:
                        self.renders.append(
                            (self.meta.font1.render(f'{data}   ', True, OUTPUT),
                            self.meta.font1.render(f'{data}   ', True, OFOCUS)))

            self.next += 1

        self.paint()

    def kick(self, event):
        if event.type == pygame.MOUSEMOTION:
            if self.in_tree(event.pos):
                if not self.focused:
                    self.focus()

                if self.tree < 0:
                    self.tree *= -1
                    self.paint_tree()

            else:
                if self.tree > 0:
                    self.tree *= -1
                    self.paint_tree(True)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.tree > 0:
                #self.log('log tree click', event)

                if event.button == pygame.BUTTON_LEFT:
                    if self.scroll:
                        scroll = self.scroll[-1]
                        if scroll[1] is not None:
                            val = scroll[0].__dict__[scroll[1]]
                            try:
                                if val.__dict__:
                                    self.scroll.append((val, None))
                                    self.tree += 1
                            except AttributeError:
                                self.img_info = self.meta.font6.render(
                                    str(val), True, EFOCUS)
                    else:
                        self.scroll.append((self.meta, 'k'))
                        self.tree += 1

                    self.render_tree()
                    self.paint_tree()

                elif event.button == pygame.BUTTON_MIDDLE:
                    python = 'self'
                    for scroll in self.scroll:
                        python += '.' + scroll[1]
                    self.meta.shell(f'python {python}')

                elif event.button == pygame.BUTTON_RIGHT:
                    if self.tree > 1:
                        self.tree -= 1
                    self.render_tree()
                    self.paint_tree(True)

                elif event.button == pygame.BUTTON_WHEELUP:
                    if self.scroll:
                        scroll = self.scroll[self.tree-2]
                        sdict = sorted(scroll[0].__dict__)
                        prev = None
                        for item in sdict:
                            if item == scroll[1]:
                                break
                            prev = item
                        if prev is None:
                            prev = sdict[-1]

                        self.scroll = self.scroll[:-1]
                        self.scroll.append((scroll[0], prev))
                        self.render_tree()
                        self.paint_tree()

                elif event.button == pygame.BUTTON_WHEELDOWN:
                    if self.scroll:
                        scroll = self.scroll[-1]
                        sdict = reversed(sorted(scroll[0].__dict__))
                        prev = None
                        for item in sdict:
                            if item == scroll[1]:
                                break
                            prev = item
                        if prev is None:
                            prev = sorted(scroll[0].__dict__)[0]

                        self.scroll = self.scroll[:-1]
                        self.scroll.append((scroll[0], prev))
                        self.render_tree()
                        self.paint_tree()

        elif event.type == pygame.MOUSEBUTTONUP:
            if self.img_info:
                self.img_info.fill(PRIMER)
                self.paint_tree()
                self.img_info = None

    def in_tree(self, pos):
        x = pos[0]
        y = pos[1]

        if x >= self.x - 5 and x <= self.x + 15 \
                and y >= self.y + self.h - 15 \
                and y <= self.y + self.h + 5:

            return True
        else:
            return False

    def render_tree(self):
        level = abs(self.tree)

        if level >= 1:
            img = self.meta.font6.render('L', True,
                TREESG if len(self.scroll) < 1 else TREEFG)

        else:
            img = self.meta.font6.render('!!!', True, EXCEPT)

        if level >= 2:
            scroll = self.scroll[0]
            items = []
            w = 0
            h = 0

            if level > 2:
                iimg = self.meta.font4.render(scroll[1], True, TREEFG)
                w = iimg.get_width()
                h += iimg.get_height()
                items.append(iimg)

            else:
                for item in sorted(scroll[0].__dict__):
                    iimg = self.meta.font3.render(item, True,
                        TREESG if scroll[1] == item else TREEFG)
                    h += iimg.get_height()
                    if iimg.get_width() > w:
                        w = iimg.get_width()
                    items.append(iimg)

            tree = pygame.Surface((w + img.get_width(), h + img.get_height()))
            tree.blit(img, (0, h))

            y = 0
            for item in items:
                tree.blit(item, (img.get_width(), y))
                y += item.get_height()

            img = tree

        if level >= 3:
            scroll = self.scroll[1]
            items = []
            w = 0
            h = 0

            for item in sorted(scroll[0].__dict__):
                iimg = self.meta.font3.render(item, True,
                    TREESG if scroll[1] == item else TREEFG)
                h += iimg.get_height()
                if iimg.get_width() > w:
                    w = iimg.get_width()
                items.append(iimg)

            tree = pygame.Surface((w + img.get_width(), h + img.get_height()))
            tree.blit(img, (0, h))

            y = 0
            for item in items:
                tree.blit(item, (img.get_width(), y))
                y += item.get_height()

            img = tree

        self.img_tree = pygame.Surface((img.get_width(), img.get_height()))
        self.img_tree.fill(TREEBG)
        self.img_tree.blit(img, (0, 0))

    def paint(self):
        self.paint_primer()
        self.paint_history()
        self.paint_tree()

    def paint_primer(self):
        pygame.draw.rect(self.meta.screen, PRIMER,
            pygame.Rect((self.x, self.y), (self.w, self.h)))

    def paint_history(self):
        height = 0
        showing = 0

        for img1, img2 in reversed(self.renders):
            img = img2 if self.focused else img1
            h = img.get_height()

            if height + h > self.h:
                break

            w = img.get_width()
            height += h
            self.meta.screen.blit(img,
                (self.x + self.w - w, self.y + self.h - height))

            showing += 1

        self.renders = self.renders[-showing:]

    def paint_tree(self, overclear=False):
        w = self.img_tree.get_width()
        h = self.img_tree.get_height()

        if self.tree < 0:
            if h > self.h and not overclear:
                h = self.h
            if w > self.w and not overclear:
                w = self.w

            pygame.draw.rect(self.meta.screen, PRIMER,
                pygame.Rect((self.x, self.y + self.h - h), (w, h)))

        elif self.tree > 0:
            self.meta.screen.blit(self.img_tree,
                (self.x, self.y + self.h - h))

            if self.img_info:
                self.meta.screen.blit(self.img_info, (self.x + w,
                    self.y + self.h - h - self.img_info.get_height()))

    def focus(self):
        super().focus()
        #self.update = True
        self.border(BLUE)
        #self.next = self.next - len(self.renders)
        #self.renders = []
        self.paint()

    def unfocus(self):
        super().unfocus()
        self.border(BLACK)
        #self.next = self.next - len(self.renders)
        #self.renders = []

