''' Operating (oK) System '''

from k.ui import *
print('YO  '+c.Style.BRIGHT+'[esc]'+c.Style.NORMAL+'APE QUITS  and   ' \
    + c.Style.BRIGHT+'<ctrl-c>'+c.Style.NORMAL+' to exit')

import k.cmd
import k.db as kdb
import k.imagine as kimg
import k.home as home
import k.video as video
#import k.game as game
import k.project as project
import k.replay as replay
from k.replay.ops import *
import k.ack as ack
import k.player as player
from k.player.actions import PlayerPlay, PlayerPause, PlayerSeek, PlayerNoteOn, PlayerNoteOff
from k.player.ops import Commands
import k.player.music as music

import sys
from datetime import datetime
import traceback
import time
from html import escape


class OS:
    def __init__(self):
        self.init_start = datetime.now()
        self.go = False

        self.testing = False
        self.imagine = True
        self.clock = Clock()
        self.square = False
        self.replays = True
        self.fullscreen = False

        if OS.dip('+'):
            print('THIS IS A TEST')
            self.testing = True

        if OS.dip('1'):
            print('no imagination')
            self.imagine = None

        if OS.dip('3'):
            print('fps//no limits')
            self.clock = NullClock()

        if OS.dip('4'):
            print('square up')
            self.square = True

        if OS.dip('6'):
            print('replay nix')
            self.replays = False

        if OS.dip('9'):
            print('full-screen')
            self.fullscreen = True

        #self.peeking = False

        pygame.mixer.pre_init(SAMPLE_RATE, -16, 1)
        pygame.init()

        # On Windows, pygame.mixer (initialized by default with pygame) can
        # exclusively lock the audio device. We quit the mixer here to free up
        # the device for the 'just_playback' library.
        pygame.mixer.quit()

        pygame.display.set_caption('k-os')

        if self.imagine:
            self.imagine = kimg.ImageEngine()
            self.imagine.start()

        # F-Key Audio Loop Tracks state
        self.f_key_loops = {}
        self.f_key_current_actions = []
        self.f_key_capturing = False

        # Auto-Tune Music Mode
        self.music = music.Mode(self)

        self.player_indicator_flash_time = 0

        self.init_stop = datetime.now()

    @staticmethod
    def dip(switch):
        if len(sys.argv) < 2:
            return False

        return switch in sys.argv[1]

    def chaos(self):
        self.init()

        try:
            while self.go:
                for event in pygame.event.get():
                    with self.rate_kick:
                        self.kick(event)

                with self.rate_tick:
                    self.tick()

                if self.imagine:
                    with self.rate_burn:
                        ie = self.imagine.burn(self.screen,
                                               pygame.image.frombuffer)
                        if ie:
                            self.lit.append(ie)

                self.see()

                if not self.clock.ready():
                    self.clock.wait()

                #    self.update_status()

                #if self.player.players and self.player.players[-1].playing:
                #    time.sleep(1)

        except KeyboardInterrupt:
            print('got keyboard interrupt')
            #self.go = False

        finally:
            self.kill()

    def init(self, screen=None):
        if screen is None:
            if not self.fullscreen:
                screen = pygame.display.set_mode((WIDTH, HEIGHT))

            else:
                screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

        pygame.scrap.init()
        pygame.scrap.set_mode(pygame.SCRAP_CLIPBOARD)

        self.screen = screen
        self.gui = KGUI((WIDTH, HEIGHT - STATUS))
        self.sui = KGUI((WIDTH, STATUS))
        self.lit = [ ]

        # Track indicator
        self.TRACK_COUNT = 12
        self.TRACK_W = 17
        self.TRACKS_W = self.TRACK_W * self.TRACK_COUNT
        self.TRACKS_H = 22
        #self.TRACKS_X = (WIDTH - self.TRACKS_W) // 2
        self.TRACKS_X = 180
        self.TRACKS_Y = (STATUS - self.TRACKS_H) // 2
        self.tracks_font = pygame.font.SysFont('monospace', 10, bold=True)
        self._draw_tracks_surfaces()

        # Samples indicator
        self.SAMPLES_COUNT = 10
        self.SAMPLES_W = self.TRACK_W * self.SAMPLES_COUNT
        self.SAMPLES_H = self.TRACKS_H
        self.SAMPLES_X = (WIDTH // 2) + ((WIDTH // 2) - (self.TRACKS_X + self.TRACKS_W))
        self.SAMPLES_Y = self.TRACKS_Y
        self.samples_font = self.tracks_font
        self._draw_samples_surfaces()

        # Player indicator
        self.PLAYER_INDICATOR_W = self.TRACK_W
        self.PLAYER_INDICATOR_H = self.TRACKS_H
        self.PLAYER_INDICATOR_X = self.SAMPLES_X + self.SAMPLES_W + 25
        self.PLAYER_INDICATOR_Y = self.TRACKS_Y
        self.player_indicator_font = self.tracks_font
        self._draw_player_indicator_surface()

        self.bg = pygame.Surface((WIDTH, HEIGHT-STATUS))
        self.bg.fill(BLACK)
        pygame.draw.line(self.bg, WHITE,
            (WIDTH-PWIDTH-1, 0), (WIDTH-PWIDTH-1, HEIGHT-STATUS-1))
        pygame.draw.line(self.bg, WHITE,
            (0, HEIGHT-STATUS-1), (WIDTH, HEIGHT-STATUS-1))
        self.bglit = None

        self.btn_home = pygame_gui.elements.UIButton(
            text='?!',
            manager=self.gui,
            relative_rect=SPACER)
        self.panel_home = home.Panel(self,
            target(self.btn_home, 'top'))

        self.cur_btn = self.btn_home
        self.cur_btn.disable()
        self.cur_panel = self.panel_home
        self.cur_panel.show()

        self.jobs = [ ]
        self.status_updated = self.init_start
        self.status('B')

        self.btn_video = pygame_gui.elements.UIButton(
            text='Video',
            anchors=target(self.btn_home),
            manager=self.gui,
            relative_rect=SPACER)
        self.panel_video = video.Panel(self,
            target(self.btn_video, 'top'))

        #self.btn_game = pygame_gui.elements.UIButton(text='Game',
        #    anchors=target(self.btn_video),
        #    manager=self.gui, relative_rect=SPACER)
        #self.panel_game = game.Panel(self,
        #    target(self.btn_replay, 'top'))

        self.btn_project = pygame_gui.elements.UIButton(
            text='Project',
            #anchors=target(self.btn_game),
            anchors=target(self.btn_video),
            manager=self.gui,
            relative_rect=SPACER)
        self.panel_project = project.Panel(self,
            target(self.btn_project, 'top'))

        if self.replays:
            self.btn_replay = pygame_gui.elements.UIButton(
                text='Replay',
                anchors=target(self.btn_project),
                manager=self.gui,
                relative_rect=SPACER)
            self.panel_replay = replay.Panel(self,
                target(self.btn_replay, 'top'))

        self.btn_ack = pygame_gui.elements.UIButton(
            text='', # blank slate (blackboard)
            manager=self.gui,
            relative_rect=pygame.Rect((WIDTH/2-15, 0), (30, 40)))
        self.ack = None

        #self.lbl_pstatus = pygame_gui.elements.UILabel(
        #    text='',
        #    manager=self.gui,
        #    relative_rect=pygame.Rect((200, HEIGHT-30), (-1, -1)))

        self.confirming = None
        self.player = player.Stack(self)
        k.cmd.install('player', Commands(self))

        self.rate_kick = Counter()
        self.rate_tick = Counter()
        self.rate_burn = Counter()
        self.rate_lit = Counter()

        self.status('N')
        self.clicked = False
        self.hovering = None
        self.closing = False
        self.escaping = False
        self.shifting = False
        self.control = False

        #if self.replays:
        #    self.gui.update(0)
        #    self.paint()
        #    self.replay_screen()

        self.init_stop = datetime.now()
        self.go = True

    def _draw_tracks_surfaces(self):
        # Helper to create a complete track bar surface with a given style
        def create_styled_surface(bg_color, text_color):
            surface = pygame.Surface((self.TRACKS_W, self.TRACKS_H))
            surface.fill(bg_color)
            for i in range(self.TRACK_COUNT):
                text_surf = self.tracks_font.render(str(i + 1), True, text_color)
                text_rect = text_surf.get_rect(center=(i * self.TRACK_W + self.TRACK_W / 2, self.TRACKS_H / 2))
                surface.blit(text_surf, text_rect)
                if i > 0:
                    pygame.draw.line(surface, GRAY, (i * self.TRACK_W, 0), (i * self.TRACK_W, self.TRACKS_H))
            pygame.draw.rect(surface, GRAY, surface.get_rect(), 1)
            return surface

        # Normal surface (black background, white numbers)
        self.tracks_surface = create_styled_surface(BLACK, WHITE)
        # Capturing surface (yellow background, black numbers)
        self.tracks_surface_capturing = create_styled_surface(YELLOW, BLACK)

    def _draw_samples_surfaces(self):
        # Helper to create a complete samples bar surface with a given style
        def create_styled_surface(bg_color, text_color):
            surface = pygame.Surface((self.SAMPLES_W, self.SAMPLES_H))
            surface.fill(bg_color)
            labels = [str(i) for i in range(1, 10)] + ['0']
            for i in range(self.SAMPLES_COUNT):
                text_surf = self.samples_font.render(labels[i], True, text_color)
                text_rect = text_surf.get_rect(center=(i * self.TRACK_W + self.TRACK_W / 2, self.SAMPLES_H / 2))
                surface.blit(text_surf, text_rect)
                if i > 0:
                    pygame.draw.line(surface, GRAY, (i * self.TRACK_W, 0), (i * self.TRACK_W, self.SAMPLES_H))
            pygame.draw.rect(surface, GRAY, surface.get_rect(), 1)
            return surface

        # Normal surface (black background, white numbers)
        self.samples_surface = create_styled_surface(BLACK, WHITE)

    def _draw_player_indicator_surface(self):
        # Helper to create the player indicator surface
        def create_surface(bg_color, text_color):
            surface = pygame.Surface((self.PLAYER_INDICATOR_W, self.PLAYER_INDICATOR_H))
            surface.fill(bg_color)
            text_surf = self.player_indicator_font.render('P', True, text_color)
            text_rect = text_surf.get_rect(center=(self.PLAYER_INDICATOR_W / 2, self.PLAYER_INDICATOR_H / 2))
            surface.blit(text_surf, text_rect)
            pygame.draw.rect(surface, GRAY, surface.get_rect(), 1)
            return surface

        # Normal surface (black background, white text)
        self.player_indicator_surface = create_surface(BLACK, WHITE)

    def tick(self, gui=True):
        #print('.', end='')
        #sys.stdout.flush()

        tdelta = self.clock.tick()

        if self.replays:
            self.panel_replay.tick()

        if self.player.big or self.ack:
            gui = False

        if gui:
            #studio = self.panel_project.panel_studio
            #if studio.project_id is None:
            #    self.lbl_pstatus.set_text("NO PROJECT")
            #elif studio.started:
            #    self.lbl_pstatus.set_text(str(datetime.now()-studio.started))
            #else:
            #    self.lbl_pstatus.set_text('PAUSED')

            self.gui.update(tdelta)
            self.paint()

            completed = 0
            for job in self.jobs:
                self.see()
                self.status(job[2])

                try:
                    if job[1] is None:
                        job[0]()

                    else:
                        job[0](*job[1])

                    if not self.confirming:
                        self.status('N')

                except Exception as e:
                    self.bug(e)
                    #self.status('E')

                tdelta = self.clock.tick()
                self.gui.update(tdelta)
                self.paint()
                completed += 1

                if self.confirming:
                    break

            del self.jobs[:completed]

            if self.confirming is False:
                self.player.resume()
                self.confirming = None

        if not self.confirming:
            self.player.tick()
            self.status()

            if self.ack and not self.player.big:
                self.ack.tick()
                #self.paint()

        if self.clicked:
            self.clicked = False
            self.replay_screen()

    def kick(self, event):
        #print(event)
        #debug_event(event)

        if event.type == pygame.QUIT:
            #self.go = False
            self.kill()

        elif event.type == pygame.WINDOWEXPOSED:
            self.status()
            #self.peek()

        elif event.type == pygame.WINDOWENTER:
            pass

        elif event.type == pygame.WINDOWLEAVE:
            pass

        elif event.type == pygame.WINDOWFOCUSGAINED:
            ##self.peek()
            pass

        elif event.type == pygame.WINDOWFOCUSLOST:
            #self.peek(False, 500)
            pass

        elif event.type == pygame.KEYDOWN:
            self.replay_op(KeyDown(event.scancode))

            alt = event.mod & pygame.KMOD_ALT
            ctrl = event.mod & pygame.KMOD_CTRL
            shift = event.mod & pygame.KMOD_SHIFT \
                or event.mod & pygame.KMOD_LSHIFT \
                or event.mod & pygame.KMOD_RSHIFT
            nomod = not alt and not ctrl and not shift

            if self.panel_home.panel_keys.discover:
                self.panel_home.panel_keys.keydown(event.key, event.mod)

            elif event.key == pygame.K_ESCAPE:
                if self.player.big:
                    self.player.size_normal()
                elif self.ack:
                    self.ack.kill()
                    self.ack = None
                    self.status('N')
                elif self.confirming:
                    self.confirming[0].kill()
                    self.confirming = None
                    self.status('N')
                    self.player.resume()
                elif self.player.is_playing(True):
                    self.player.pause()
                    self.closing = True
                else:
                    self.escaping = True
                    self.status('Q')

            elif self.f_key_capturing and event.key >= pygame.K_F1 and event.key <= pygame.K_F12:
                # Loop capture is finished, calculate duration from now.
                first_action_time = self.f_key_current_actions[0].t
                last_action_time = time.perf_counter()
                duration = last_action_time - first_action_time

                # If other loops are active, conform the duration of this new loop
                # to maintain rhythmic synchronization.
                active_loop_players = self.player.loop_players.values()
                if active_loop_players:
                    # Ratios derived from user request (multiples of 2 and 3)
                    # for finding musically-related loop lengths.
                    ratios = [
                        1/4, 1/3, 1/2, 2/3, 3/4, 1.0, 4/3, 3/2, 2.0, 3.0, 4.0
                    ]

                    best_conformed_duration = duration
                    min_diff = float('inf')

                    # Find the best fit among all active loops and all candidate durations.
                    for player in active_loop_players:
                        active_duration = player.duration
                        if active_duration <= 0:
                            continue

                        # 1. Check against explicit musical ratios
                        for ratio in ratios:
                            candidate_duration = active_duration * ratio
                            diff = abs(candidate_duration - duration)
                            if diff < min_diff:
                                min_diff = diff
                                best_conformed_duration = candidate_duration

                        # 2. Check against nearest integer multiples/divisions.
                        # This helps snap to the beat for longer or shorter loops.
                        if duration > active_duration:
                            multiple = round(duration / active_duration)
                            if multiple > 1: # Don't re-check ratio of 1.0
                                candidate_duration = active_duration * multiple
                                diff = abs(candidate_duration - duration)
                                if diff < min_diff:
                                    min_diff = diff
                                    best_conformed_duration = candidate_duration
                        else: # duration <= active_duration
                            divisor = round(active_duration / duration)
                            if divisor > 1:
                                candidate_duration = active_duration / divisor
                                diff = abs(candidate_duration - duration)
                                if diff < min_diff:
                                    min_diff = diff
                                    best_conformed_duration = candidate_duration

                    # If a better duration was found, use it.
                    if abs(duration - best_conformed_duration) > 1e-9: # Compare floats carefully
                        print(f"Loop duration conformed. Original: {duration:.3f}s -> New: {best_conformed_duration:.3f}s")
                        duration = best_conformed_duration

                # Save captured actions to an F-Key track
                music_context = None
                if self.music.active and self.music.sample:
                    music_context = {
                        'sample': self.music.sample,
                        'start_frame': self.music.sample_start_frame,
                        'end_frame': self.music.sample_end_frame,
                        'base_fps': self.music.base_fps,
                    }

                current_volume = 1.0 # Default
                if self.player.players:
                    active_player = self.player.players[-1]
                    actual_player = getattr(active_player, 'go', active_player)
                    if hasattr(actual_player, 'volume'):
                        current_volume = actual_player.volume

                self.f_key_loops[event.key] = (self.f_key_current_actions, duration, music_context, current_volume)
                if event.key in self.player.loop_players:
                    self.player.toggle_loop(event.key, None) # Disable if it was running
                self.f_key_capturing = False
                print(f"Loop saved to {pygame.key.name(event.key)}. "
                      f"({len(self.f_key_current_actions)} actions, duration: {duration:.2f}s, vol: {current_volume:.2f})")
                self.f_key_current_actions = []
                self.status()

            elif event.key == pygame.K_CAPSLOCK:
                self.music.toggle()

            elif event.key == pygame.K_INSERT:
                self.f_key_capturing = not self.f_key_capturing
                if self.f_key_capturing:
                    # Determine initial state of the player to start recording correctly.
                    initial_action = PlayerPause()  # Default action
                    if self.player.players and self.player.players[-1].playing:
                        active_player = self.player.players[-1]
                        # Let's use the new method on the player to get/create it.
                        # This works for both Chaos players and Video players.
                        frag_id = active_player.get_or_create_frag_id()
                        if frag_id is not None:
                            actual_player = getattr(active_player, 'go', active_player)
                            current_frame = actual_player.trk.frame
                            initial_action = PlayerPlay(frag_id, start_frame=current_frame)

                    self.f_key_current_actions = [initial_action]
                    print("Capturing started... Press F1-F12 to save, or INSERT to cancel.")
                else:  # Cancelled
                    self.f_key_current_actions = []
                    print("Capturing cancelled.")
                self.status()

            elif not self.confirming:
                if self.escaping:
                    self.escaping = False
                    self.status('N')

                elif self.closing:
                    self.closing = False

                elif event.key == pygame.K_BREAK:
                    if nomod and self.replays:
                        self.replay_break()
                        self.job(self.panel_replay.panel_library.refresh)

                elif event.key == pygame.K_TAB:
                    if shift:
                        self.score()

                else:
                    if self.music.active and self.music.keydown(event.key):
                        # Music mode handled the key, do nothing more.
                        pass
                    else:
                        # Default event handling
                        self.player.keydown(event.key, event.mod)

                        if not self.ack and not self.player.big:
                            self.cur_panel.keydown(event.key, event.mod)

                            if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                                self.shifting = True

                            elif event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                                self.control = True

        elif event.type == pygame.KEYUP:
            self.replay_op(KeyUp(event.scancode))

            if self.panel_home.panel_keys.discover:
                self.panel_home.panel_keys.keyup(event.key, event.mod)

            elif event.key == pygame.K_ESCAPE:
                if self.escaping:
                    #self.go = False
                    self.kill()

                elif self.closing:
                    self.player.killall()

            elif not self.confirming:
                if not self.f_key_capturing and event.key >= pygame.K_F1 and event.key <= pygame.K_F12:
                    # Toggle F-Key loop playback
                    self.player.toggle_loop(event.key, self.f_key_loops.get(event.key))
                    self.status()
                elif self.music.active and self.music.keyup(event.key):
                    # Music mode handled the key, do nothing more.
                    pass
                else:
                    self.player.keyup(event.key, event.mod)

                    if not self.ack and not self.player.big:
                        self.cur_panel.keyup(event.key, event.mod)

                    if event.key == pygame.K_LSHIFT \
                            or event.key == pygame.K_RSHIFT:
                        self.shifting = False

                    elif event.key == pygame.K_LCTRL \
                            or event.key == pygame.K_RCTRL:
                        self.control = False

        elif event.type == pygame.MOUSEMOTION:
            self.replay_op(MouseMove(event.pos[0], event.pos[1]))

        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.replay_op(MouseDown(event.button))
            self.player.mouse_down(event)

        elif event.type == pygame.MOUSEBUTTONUP:
            self.replay_op(MouseUp(event.button))
            self.player.mouse_up(event)

            if event.button == pygame.BUTTON_RIGHT:
                self.replay_capture_toggle()

            elif event.button == pygame.BUTTON_WHEELUP \
                    or event.button == pygame.BUTTON_WHEELDOWN:
                self.clicked = True

        elif event.type == pygame_gui.UI_BUTTON_ON_HOVERED:
            if not self.hovering is event.ui_element:
                self.hovering = event.ui_element
                self.replay_screen()

        elif event.type == pygame_gui.UI_BUTTON_ON_UNHOVERED:
            if self.hovering is event.ui_element:
                self.hovering = None
                self.replay_screen()

        elif event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.replay_screen()

        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            if not self.player.big:
                if event.ui_element is self.btn_home:
                    self.panel_swap(self.btn_home, self.panel_home)

                elif event.ui_element is self.btn_video:
                    self.panel_swap(self.btn_video, self.panel_video)

                #elif event.ui_element is self.btn_game:
                #    self.panel_swap(self.btn_game, self.panel_game)

                elif event.ui_element is self.btn_project:
                    self.panel_swap(self.btn_project, self.panel_project)

                elif self.replays and event.ui_element is self.btn_replay:
                    self.panel_swap(self.btn_replay, self.panel_replay)

                elif event.ui_element is self.btn_ack:
                    self.ack = ack.Blackboard(self)
                    self.status('A')

                else:
                    self.cur_panel.click(event.ui_element)

            self.player.click(event.ui_element)
            self.clicked = True

        elif event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
            self.replay_screen()

        elif event.type == pygame_gui.UI_TEXT_BOX_LINK_CLICKED:
            if event.link_target.lower().startswith('http://') \
                    or event.link_target.lower().startswith('https://'):
                self.click_link(event.link_target)

            else:
                self.cur_panel.click(event.ui_element, event.link_target)
                self.player.click(event.ui_element, event.link_target)

        elif event.type == pygame_gui.UI_WINDOW_CLOSE:
            if self.confirming and event.ui_element == self.confirming[0]:
                self.confirming[0].kill()
                self.confirming = None
                self.status('N')
                self.player.resume()

        elif event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
            if self.confirming and event.ui_element == self.confirming[0]:
                self.confirming[0].kill()
                fn = self.confirming[1]
                self.confirming = False
                self.job(fn)

        if self.ack:
            self.ack.kick(event)

        elif not self.player.big:
            self.gui.process_events(event)

    def paint(self):
        lit = self.screen.blit(self.bg, (0, 0))
        if self.bglit:
            self.lit.extend(self.bglit)
        else:
            self.lit.append(pygame.Rect(lit))

        if not self.ack:
            self.gui.draw_ui(self.screen)

    def blit(self, surface, position, area=None):
        lit = self.screen.blit(surface, position, area)
        self.lit.append(pygame.Rect(lit))

    def see(self):
        if self.lit or self.confirming:
            with self.rate_lit:
                if self.confirming: pygame.display.flip()
                else: pygame.display.update(self.lit)
                self.lit = [ ]

    def flash_player_indicator(self):
        self.player_indicator_flash_time = time.perf_counter()

    def status(self, mode=None):
        update = datetime.now()

        if mode != 'K' and self.panel_home.panel_keys.discover:
            self.panel_home.panel_keys.toggle_discover()

        if mode == 'N':
            pygame.mouse.set_cursor(*pygame.cursors.arrow)
        elif mode == 'B':
            #pygame.mouse.set_cursor(*pygame.cursors.tri_left)
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_WAITARROW)
        elif mode == 'D':
            #pygame.mouse.set_cursor(*pygame.cursors.tri_right)
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_WAIT)
        elif mode == 'E':
            #pygame.mouse.set_cursor(*pygame.cursors.broken_x)
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_NO)
        #elif mode == 'A':
        #    #pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        #    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
        elif mode == 'S':
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        elif mode == 'K':
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        elif mode == 'C':
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        elif mode == 'U':
            pygame.mouse.set_cursor(*pygame.cursors.arrow)

        if mode is not None:
            for status in self.panel_home.status:
                self.panel_home.status[status].hide()
            self.panel_home.status[mode].show()

        self.sui.update((update - self.status_updated).total_seconds())
        self.status_updated = update

        bar = pygame.Surface((WIDTH, STATUS))
        self.sui.draw_ui(bar)

        if hasattr(self, 'player'):
            # Draw F-Key Tracks indicator
            if self.f_key_capturing:
                bar.blit(self.tracks_surface_capturing, (self.TRACKS_X, self.TRACKS_Y))
            else:
                bar.blit(self.tracks_surface, (self.TRACKS_X, self.TRACKS_Y))

            for i in range(self.TRACK_COUNT):
                key = pygame.K_F1 + i
                track_x = self.TRACKS_X + i * self.TRACK_W
                track_y = self.TRACKS_Y

                color = None
                volume = 0.0

                if key in self.player.loop_players:
                    loop_player = self.player.loop_players[key]
                    volume = loop_player.volume
                    if loop_player.will_loop:
                        color = BLUE
                    else:
                        color = GREEN
                elif key in self.f_key_loops:
                    volume = self.f_key_loops[key][3]
                    color = RED

                if color:
                    # Draw border for this specific key
                    key_rect = pygame.Rect(track_x, track_y, self.TRACK_W, self.TRACKS_H)
                    pygame.draw.rect(bar, color, key_rect, 1)

                    # Draw volume-based background, inside the border
                    if volume > 0:
                        # Height is scaled by volume. We subtract 2 to account for 1px top/bottom border.
                        fill_height = int((self.TRACKS_H - 2) * volume)
                        if fill_height > 0:
                            # Position from the bottom up
                            rect_fill = pygame.Rect(
                                track_x + 1,
                                track_y + 1 + (self.TRACKS_H - 2 - fill_height),
                                self.TRACK_W - 2,
                                fill_height
                            )
                            bar.fill(color, rect_fill)

                    # Determine text color and re-draw text
                    text_color = WHITE
                    if color in [GREEN, RED]:
                        text_color = BLACK

                    text_surf = self.tracks_font.render(str(i + 1), True, text_color)
                    text_rect = text_surf.get_rect(center=(track_x + self.TRACK_W / 2, track_y + self.TRACKS_H / 2))
                    bar.blit(text_surf, text_rect)

            # Draw Samples and Player indicators
            if self.player.players:
                # Draw Samples indicator
                bar.blit(self.samples_surface, (self.SAMPLES_X, self.SAMPLES_Y))
                player = self.player.players[-1]
                actual_player = getattr(player, 'go', player)

                if hasattr(actual_player, 'selection_regions'):
                    selection_regions = actual_player.selection_regions
                    active_slot_key = self.music.active_slot_key if self.music.active else None

                    sample_keys = [pygame.K_1 + i for i in range(9)] + [pygame.K_0]
                    labels = [str(i) for i in range(1, 10)] + ['0']

                    for i, key in enumerate(sample_keys):
                        sample_x = self.SAMPLES_X + i * self.TRACK_W
                        sample_y = self.SAMPLES_Y

                        color = None
                        volume = 0.0

                        if key == active_slot_key:
                            color = GREEN
                            volume = self.music.volume
                        elif key in selection_regions:
                            color = RED
                            region_data = selection_regions[key]
                            volume = region_data[2] if len(region_data) > 2 else 1.0

                        if color:
                            # Draw border
                            key_rect = pygame.Rect(sample_x, sample_y, self.TRACK_W, self.SAMPLES_H)
                            pygame.draw.rect(bar, color, key_rect, 1)

                            # Draw volume-based background
                            if volume > 0:
                                fill_height = int((self.SAMPLES_H - 2) * volume)
                                if fill_height > 0:
                                    rect_fill = pygame.Rect(
                                        sample_x + 1,
                                        sample_y + 1 + (self.SAMPLES_H - 2 - fill_height),
                                        self.TRACK_W - 2,
                                        fill_height
                                    )
                                    bar.fill(color, rect_fill)

                            # Redraw text (always black for red/green sample indicators)
                            text_surf = self.samples_font.render(labels[i], True, BLACK)
                            text_rect = text_surf.get_rect(center=(sample_x + self.TRACK_W / 2, sample_y + self.SAMPLES_H / 2))
                            bar.blit(text_surf, text_rect)

                # Draw Player indicator
                bar.blit(self.player_indicator_surface, (self.PLAYER_INDICATOR_X, self.PLAYER_INDICATOR_Y))

                is_playing = getattr(actual_player, 'playing', None)
                color = GREEN if is_playing else RED
                volume = getattr(actual_player, 'volume', 0.0)
                text_color = BLACK
                direction = getattr(actual_player, 'playback_direction', 1)
                speed = getattr(actual_player, 'playback_speed', 1.0)

                # Flash blue on seek/jump
                flash_duration = 0.05 # 50ms
                if time.perf_counter() - self.player_indicator_flash_time < flash_duration:
                    color = BLUE
                    text_color = WHITE

                # Draw border
                key_rect = pygame.Rect(self.PLAYER_INDICATOR_X, self.PLAYER_INDICATOR_Y, self.PLAYER_INDICATOR_W, self.PLAYER_INDICATOR_H)
                pygame.draw.rect(bar, color, key_rect, 1)

                # Draw volume-based background
                if volume > 0:
                    fill_height = int((self.PLAYER_INDICATOR_H - 2) * volume)
                    if fill_height > 0:
                        rect_fill = pygame.Rect(
                            self.PLAYER_INDICATOR_X + 1,
                            self.PLAYER_INDICATOR_Y + 1 + (self.PLAYER_INDICATOR_H - 2 - fill_height),
                            self.PLAYER_INDICATOR_W - 2,
                            fill_height
                        )
                        bar.fill(color, rect_fill)

                # Redraw text
                if direction == 1:
                    indicator_text = ">>" if speed > 1.0 else ">"
                else:  # direction == -1
                    indicator_text = "<<" if speed > 1.0 else "<"
                text_surf = self.player_indicator_font.render(indicator_text, True, text_color)
                text_rect = text_surf.get_rect(center=(self.PLAYER_INDICATOR_X + self.PLAYER_INDICATOR_W / 2, self.PLAYER_INDICATOR_Y + self.PLAYER_INDICATOR_H / 2))
                bar.blit(text_surf, text_rect)


        lit = self.screen.blit(bar, (0, HEIGHT-STATUS))
        pygame.display.update(lit)

    def panel_swap(self, btn, panel):
        self.status('B')

        #if self.cur_panel == self.panel_project:
        #    if self.panel_project.cur_panel == self.panel_project.panel_studio:
        #        self.panel_project.panel_studio.suspend()

        if self.cur_btn:
            self.cur_btn.enable()
        self.cur_btn = btn
        if self.cur_btn:
            self.cur_btn.disable()

        self.cur_panel.hide()
        self.cur_panel = panel
        self.cur_panel.show()

        self.status('N')

    def click_link(self, link):
        print(f'LINK CLICK: {link}')

        llink = link.lower()
        start = llink.index('://') + 3
        llink = llink[start:]

        if llink.startswith('www.'):
            llink = llink[4:]

        if llink.startswith('youtube.com/watch?v=') \
                or llink.startswith('youtu.be/'):

            self.panel_swap(self.btn_video, self.panel_video)
            panel = self.panel_video
            panel.panel_swap(panel.btn_youtube, panel.panel_youtube)
            panel = panel.panel_youtube
            panel.clear_results()
            panel.input.set_text(link)
            panel.btn_video.disable()

            self.job(panel.get_video, 'D')

    def bug(self, e):
        print('*!*!* UNCAUGHT EXCEPTION *!*!*')
        print(e)

        formatted = traceback.format_exc()
        print(formatted)

        formatted = f'<b>{e}</b><br><br>' \
                    + escape(formatted).replace('\n', '<br>')

        self.confirm(self.kill, 'Error Occurred', 'Quit', formatted,
            (200, 100), (WIDTH-400, HEIGHT-STATUS-200))

        self.status('E')

    def score(self):
        print(' '+c.Style.DIM+'[  ]'+c.Style.NORMAL \
            + ' scores are fps/% in 1s, 5s, 15s increments:')
        score = ' '+c.Style.DIM+'[OK]'+c.Style.NORMAL \
            + '    '+c.Fore.WHITE+c.Back.BLACK+c.Style.BRIGHT+'tick' \
            + c.Style.RESET_ALL+f' {self.rate_tick}' \
            + '    '+c.Fore.WHITE+c.Back.BLACK+c.Style.BRIGHT+'kick' \
            + c.Style.RESET_ALL+f' {self.rate_kick}'
        if self.imagine:
            score += '    '+c.Fore.WHITE+c.Back.BLACK+c.Style.BRIGHT+'burn' \
                + c.Style.RESET_ALL+f' {self.rate_burn}'
        score += '    '+c.Fore.WHITE+c.Back.BLACK+c.Style.BRIGHT+'lit' \
            + c.Style.RESET_ALL+f' {self.rate_lit}'
        print(score)

        if self.imagine:
            self.imagine.score()

        self.status()

    def confirm(self, fn, title, ok, descr='', pos=(250, 200), size=(350, 250)):
        if self.confirming:
            self.confirming[0].kill()

        self.player.size_normal()
        if self.player.is_playing:
            self.player.suspend()

        self.confirming = (
            pygame_gui.windows.UIConfirmationDialog(
                window_title=title,
                manager=self.gui,
                action_short_name=ok,
                action_long_desc=descr,
                blocking = True,
                rect=pygame.Rect(pos, size)),
            fn
        )

        # resizable window interferes with our chosen mouse cursor
        self.confirming[0].resizable = False

        self.status('C')

    def job(self, fn, mode='B'):
        self.jobs.append((fn, None, mode))

    def jab(self, fn, args, mode='B'):
        self.jobs.append((fn, args, mode))

    def focus_video(self, video_id):
        video = self.panel_video
        library = video.panel_library
        library.refresh_video(video_id)
        video.panel_swap(video.btn_library, library)
        self.panel_swap(self.btn_video, video)

    def focus_keyword(self, keyword):
        video = self.panel_video
        library = video.panel_library
        library.inp_search.set_text(keyword)
        library.refresh_videos(search_keyword=keyword)
        video.panel_swap(video.btn_library, library)
        self.panel_swap(self.btn_video, video)

    def project(self):
        return self.panel_project.panel_studio.init_project()

    def frag(self, media, source, begin=None, end=None):
        project = self.project()
        return kdb.insert_frag(project, media, source, begin, end)

    def clip(self, frag, loop, loop_begin, loop_end, jumps):
        loop = '1' if loop else '0'
        loop += f',{loop_begin}'
        loop += f',{loop_end}'
        jumps = ','.join([str(j) for j in jumps])

        kdb.insert_clip(frag, loop, jumps)
        self.panel_project.panel_studio.panel_clip.add_clip(frag)

    def clip_naked(self, frag):
        kdb.insert_clip(frag, None, None)
        self.panel_project.panel_studio.panel_clip.add_clip(frag)

    def focus_clip(self, clip):
        self.panel_swap(self.btn_project, self.panel_project)

        panel = self.panel_project
        panel.panel_swap(panel.btn_studio, panel.panel_studio)

        panel = panel.panel_studio
        panel.panel_swap(panel.btn_clip, panel.panel_clip)

    def seq(self):
        return self.panel_project.panel_studio.panel_seq.panel_editor.init_seq()

    def seg(self, frag):
        seq = self.seq()
        idx = kdb.get_last_segment_idx(seq)
        if idx is None:
            idx = 0
        else:
            idx += 1

        kdb.insert_segment(seq, idx, frag)
        self.panel_project.panel_studio.panel_seq.panel_editor.add_seg(idx)

        return idx

    def focus_seg(self, seg):
        self.panel_swap(self.btn_project, self.panel_project)

        panel = self.panel_project
        panel.panel_swap(panel.btn_studio, panel.panel_studio)

        panel = panel.panel_studio
        panel.panel_swap(panel.btn_seq, panel.panel_seq)

        panel = panel.panel_seq
        panel.panel_swap(panel.btn_editor, panel.panel_editor)

    def replay_op(self, op):
        if self.replays:
            self.panel_replay.op(op)

    def replay_screen(self):
        if self.replays:
            self.panel_replay.screen()

    def replay_capture_toggle(self):
        if self.replays:
            if self.panel_replay.toggle_capture():
                self.panel_replay.init_replay()
                self.clicked = True
            else:
                self.panel_replay.screen()
                self.panel_replay.op(StopCapture())

            self.panel_replay.update_timer()

    def replay_break(self):
        if self.replays:
            self.panel_replay.break_replay()

    '''
    def peek(self, me=True, delay=None):
        if self.player.is_playing():
            return

        if self.peeking and self.peeking.poll() is None:
            # previous peek() process is still running
            return

        self.peeking = media.focus_peek(me=me, delay=delay)
    '''

    def kill(self):
        if not self.go: return
        self.go = False

        self.replay_break()

        ''' Nope: bad idea... '''
        #for job in self.jobs:
        #    self.status(job[1])
        #    try:
        #        job[0]()

        #    except Exception as e:
        #        self.bug(e)

        if self.imagine:
            print('choke image engine... ', end='')
            sys.stdout.flush()
            self.imagine.choke()
            self.imagine.join()

        print('clean up base... ', end='')
        sys.stdout.flush()
        kdb.close()
        print('done')

        #pygame.quit()
        print('graceful death')
