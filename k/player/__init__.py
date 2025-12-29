from k.ui import *
from .loop import LoopPlayer


class Stack():
    def __init__(self, k):
        self.k = k
        self.players = [ ]
        self.loop_players = {}
        self.suspended = [ ]

        #self.fps = None

        self.bigbg = pygame.Surface((WIDTH, HEIGHT - STATUS))
        self.bigbg.fill((9, 18, 81))
        self.size_normal(True)

    def kill(self):
        if not self.players:
            return

        self.pop().kill()

    def killall(self, replace=False):
        if not self.players:
            return

        for p in self.players:
            p.kill(replace)

        for p in self.loop_players.values():
            p.kill()

        self.loop_players = {}

        self.players = []

    def open(self, player, stacked=False):
        if stacked:
            if self.players:
                self.players[-1].hide()
        else:
            self.killall(True)
            self.players = []

        self.players.append(player)

        if self.big:
            player.size_to_fit(WIDTH, HEIGHT - STATUS)
        else:
            player.size_to_fit(PWIDTH, PHEIGHT)

    def pop(self):
        if not self.players:
            return None

        player = self.players.pop()

        #if self.players:
        #    self.fps = self.players[-1].fps
        #else:
        #    self.fps = None

        return player

    def remove(self, player):
        try:
            idx = self.players.index(player)
            del self.players[idx]

            #if idx == len(self.players):
            #    if idx > 0:
            #        self.fps = self.players[-1].fps
            #    else:
            #        self.fps = None

        except ValueError:
            pass

    def is_playing(self, or_paused=False):
        for player in self.players:
            if player.playing or (or_paused and player.playing == False):
                return True

        return False

    def suspend(self):
        self.suspended = []
        for player in self.players:
            if player.playing:
                player.pause()
                self.suspended.append(player)

    def resume(self):
        for player in self.suspended:
            player.play()

    def play(self):
        if not self.players:
            return

        self.players[-1].play()

    def pause(self):
        if not self.players:
            return

        self.players[-1].pause()

    def stop(self):
        if not self.players:
            return

        self.players[-1].stop()

    def tick(self):
        if not self.players:
            # Tick loops even if main player isn't active
            for player in self.loop_players.values():
                player.tick()
            return bool(self.loop_players)

        for player in reversed(self.players):
            player.tick()

        for player in self.loop_players.values():
            player.tick()

    def toggle_loop(self, key, actions):
        key_name = pygame.key.name(key).upper()
        if key in self.loop_players:
            self.loop_players[key].kill()
            del self.loop_players[key]
            print(f"Loop {key_name} disabled.")
        elif actions:
            player = LoopPlayer(self.k, key, actions)
            self.loop_players[key] = player
            player.play()
            print(f"Loop {key_name} enabled.")

    def toggle_size(self):
        if self.big:
            self.size_normal()
        else:
            self.size_big()

    def size_normal(self, force=False):
        if not force and not self.big:
            return

        self.k.blit(self.bigbg, (0, 0))

        for player in self.players:
            player.size_to_fit(PWIDTH, PHEIGHT)

        self.k.bglit = [
            pygame.Rect(0, 0, WIDTH-PWIDTH, HEIGHT-STATUS),
            pygame.Rect(WIDTH-PWIDTH, PHEIGHT, PWIDTH, HEIGHT-STATUS-PHEIGHT)
        ]

        if self.k.ack:
            self.k.ack.paint()

        self.big = False

    def size_big(self):
        if self.big:
            return

        self.k.blit(self.bigbg, (0, 0))

        for player in self.players:
            player.size_to_fit(WIDTH, HEIGHT - STATUS)

        self.k.bglit = [
            pygame.Rect(0, HEIGHT-STATUS, WIDTH, STATUS),
        ]

        self.big = True

    def click(self, element, target=None):
        if not self.players:
            return

        self.players[-1].click(element, target)

    #def click_link(self, target):
    #    if not self.players:
    #        return

    #    if target.startswith('caption_'):
    #        start = target[8:]
    #        self.players[-1].seek_millis(int(start))

    def mouse_down(self, event):
        if not self.players:
            return

        self.players[-1].mouse_down(event)

    def mouse_up(self, event):
        if not self.players:
            return

        self.players[-1].mouse_up(event)

    def keydown(self, key, mod):
        if key == pygame.K_SCROLLOCK:
            self.toggle_size()

        if not self.players:
            return

        if key == pygame.K_DELETE:
            self.kill()

        else:
            self.players[-1].keydown(key, mod)

    def keyup(self, key, mod):
        if not self.players:
            return

        self.players[-1].keyup(key, mod)