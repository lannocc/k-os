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
import k.online as online
import k.ack as ack
import k.player as player
from k.player.ops import Commands

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
        self.local = False
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

        if OS.dip('2'):
            print('stay local')
            self.local = True

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

        if not self.local:
            self.panel_online = online.Panel(self,
                target(self.btn_project, 'top'))

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
        self.music_mode = False

        #if self.replays:
        #    self.gui.update(0)
        #    self.paint()
        #    self.replay_screen()

        self.init_stop = datetime.now()
        self.go = True

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

        if not self.local:
            self.panel_online.tick()

        if not self.confirming:
            self.player.tick()

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

            elif not self.confirming:
                if self.escaping:
                    self.escaping = False
                    self.status('N')

                elif self.closing:
                    self.closing = False

                elif event.key == pygame.K_BREAK:
                    if nomod and self.replays:
                        self.replay_break()
                        self.job(self.panel_replay.refresh)

                elif event.key == pygame.K_TAB:
                    if shift:
                        self.score()

                else:
                    self.player.keydown(event.key, event.mod)

                    if not self.ack and not self.player.big:
                        if not self.music_mode:
                            self.cur_panel.keydown(event.key, event.mod)

                        if event.key == pygame.K_LSHIFT \
                                or event.key == pygame.K_RSHIFT:
                            self.shifting = True

                        elif event.key == pygame.K_LCTRL \
                                or event.key == pygame.K_RCTRL:
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

            if not self.local:
                self.panel_online.mouse_button_down(event)

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
        elif mode == 'K':
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        elif mode == 'C':
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

        if mode is not None:
            for status in self.panel_home.status:
                self.panel_home.status[status].hide()
            self.panel_home.status[mode].show()

        self.sui.update((update - self.status_updated).total_seconds())
        self.status_updated = update

        bar = pygame.Surface((WIDTH, STATUS))
        self.sui.draw_ui(bar)

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

        if not self.local:
            self.panel_online.go_offline()

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