from k.ui import *
import k.db as kdb
import k.storage as media
from k.home import IMAGE
from k.replay.ops import Action
from .core import get_size_to_fit

import random


PRECT = pygame.Rect((WIDTH-PWIDTH, 0), (PWIDTH, HEIGHT))
VPRECT = pygame.Rect((PRECT[0], PRECT[1]), (PRECT[2], 313))
PRACK = pygame.Rect((140, 370), (PWIDTH-150, HEIGHT-STATUS-380))
CRACK = pygame.Rect((0, 35), (PRACK[2], PRACK[3]-35))

MOD_MAN = 666


class Player(KPanel):
    def __init__(self, k, tracker, thumbnail=None, loop=None, jumps=None):
        super().__init__(k, relative_rect=PRECT, visible=1)

        self.trk = tracker

        self.progress = pygame_gui.elements.UIHorizontalSlider(
            start_value=0,
            value_range=(0, self.trk.frames-1),
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((0, 315), (PWIDTH, 20)))

        self.btn_pp = pygame_gui.elements.UIButton(
            text='',
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((10, 335), (80, -1)))

        if hasattr(self, 'save'):
            self.btn_save = pygame_gui.elements.UIButton(
                text='Save*',
                manager=k.gui,
                container=self.container,
                relative_rect=pygame.Rect((110, 335), (80, -1)))
        else:
            self.btn_save = None

        if hasattr(self, 'clip'):
            self.btn_clip = pygame_gui.elements.UIButton(
                text='Clip',
                manager=k.gui,
                container=self.container,
                relative_rect=pygame.Rect((200, 335), (60, -1)))
        else:
            self.btn_clip = None

        if hasattr(self, 'seq'):
            self.btn_seq = pygame_gui.elements.UIButton(
                text='Seq',
                manager=k.gui,
                container=self.container,
                relative_rect=pygame.Rect((260, 335), (50, -1)))
        else:
            self.btn_seq = None

        self.lbl_frame = pygame_gui.elements.UILabel(
            text='',
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((420, 335), (-1, -1)))

        if loop:
            loop = loop.split(',')
            self.loop = True if int(loop[0])==1 else False
            self.loop_begin = int(loop[1])
            self.loop_end = int(loop[2])
        else:
            self.loop = False
            self.loop_begin = 0
            self.loop_end = self.trk.frames - 1

        self.selection_regions = {}
        self.selection_key_map = {
            pygame.K_1: '1', pygame.K_2: '2', pygame.K_3: '3', pygame.K_4: '4', pygame.K_5: '5',
            pygame.K_6: '6', pygame.K_7: '7', pygame.K_8: '8', pygame.K_9: '9', pygame.K_0: '0',
            pygame.K_BACKQUOTE: '`'
        }
        self.selection_slot_order = [
            pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5,
            pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0
        ]
        self.next_selection_slot_index = 0

        if jumps:
            self.jumps = [int(j) for j in jumps.split(',')]
        else:
            self.jumps = []
            for j in range(1, 10):
                self.jumps.append(int(j * self.trk.frames / 10))

        self.lbl_jumps = []
        for j, frame in enumerate(self.jumps):
            x = 28+round((PWIDTH-65)*frame/self.trk.frames)
            self.lbl_jumps.append(pygame_gui.elements.UILabel(
                text=str(j+1),
                manager=k.gui,
                container=self.container,
                relative_rect=pygame.Rect((x, 295), (-1, -1))))

        self.loop_bar = pygame.Surface((PWIDTH, 3))
        self.draw_loop_bar()

        self.thumb_orig = thumbnail
        self.thumb = self.thumb_orig

        self.btn_chaos = pygame_gui.elements.UIButton(
            text='?!',
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((10, 370), (120, 25)))
        self.panel_chaos = Chaos(self)

        self.cur_btn = self.btn_chaos
        self.cur_btn.disable()
        self.cur_panel = self.panel_chaos

        # For music mode override
        self.music_mode_override = False
        self.music_mode_loop_begin = 0
        self.music_mode_loop_end = 0

        # For hold-to-loop override on number keys
        self.hold_loop_override = False
        self.hold_loop_key = None
        self.hold_loop_begin = 0
        self.hold_loop_end = 0

        self.reset()

    def reset(self):
        self.progress.disable()
        self.progress.set_current_value(0)
        self.btn_pp.set_text('PLAY')
        self.lbl_frame.set_text(f'[{self.trk.frames}]')

        #self.holding = 0
        self.holding = [ ]
        self.pdrag = False

        self.music_mode_override = False
        self.hold_loop_override = False
        self.hold_loop_key = None

        self.trk.reset()
        self.img = None
        self.playing = None

    def kill(self, replace=False):
        self.stop(replace)

        self.progress.kill()
        self.btn_pp.kill()
        if self.btn_save:
            self.btn_save.kill()
        if self.btn_clip:
            self.btn_clip.kill()
        if self.btn_seq:
            self.btn_seq.kill()
        self.lbl_frame.kill()
        for lbl_jump in self.lbl_jumps:
            lbl_jump.kill()

        super().kill()

    def get_or_create_frag_id(self):
        """
        Returns the frag_id if it exists. If not, and if this is a video player,
        creates a new fragment based on the current loop selection and returns its ID.
        """
        frag_id = getattr(self, 'frag_id', None)
        if frag_id is None:
            video_id = getattr(self, 'video_id', None)
            if video_id is not None:
                # Create an implicit fragment for the current media
                #start_frame = self.trk.begin + self.loop_begin
                #end_frame = self.trk.begin + self.loop_end
                start_frame = self.trk.begin
                end_frame = self.trk.end
                frag_id = self.k.frag(kdb.MEDIA_VIDEO, video_id, start_frame, end_frame)

                # Cache it on the player instance to avoid re-creating it
                self.frag_id = frag_id
        return frag_id

    def play(self):
        if self.playing:
            return

        if self.k.f_key_capturing:
            from k.player.actions import PlayerPlay
            # The action is recorded based on the new state
            frag_id = self.get_or_create_frag_id()
            if frag_id is not None:
                current_frame = self.trk.frame
                self.k.f_key_current_actions.append(PlayerPlay(frag_id, start_frame=current_frame))

        self.op_start()
        self.progress.enable()
        self.btn_pp.set_text('PAUSE')

        # User request: ensure volume is reset on play/resume, and music mode override is off
        if hasattr(self.trk, 'res') and hasattr(self.trk.res, 'audio'):
            self.trk.res.audio.set_volume(1.0)
        self.music_mode_override = False

        self.trk.play()
        self.playing = True

    def pause(self):
        if not self.playing:
            return

        if self.k.f_key_capturing:
            from k.player.actions import PlayerPause
            self.k.f_key_current_actions.append(PlayerPause())

        self.op_stop()
        self.btn_pp.set_text('RESUME')

        self.trk.pause()
        self.playing = False

    def stop(self, replace=False):
        if self.playing is None:
            return

        if self.k.f_key_capturing:
            from k.player.actions import PlayerStop
            self.k.f_key_current_actions.append(PlayerStop())

        self.reset()

        if not replace:
            self.op_stop()
            self.k.replay_break()

    def seek(self, frame):
        if self.k.f_key_capturing:
            from k.player.actions import PlayerSeek
            # Record absolute frame number for the tracker
            self.k.f_key_current_actions.append(PlayerSeek(frame + self.trk.begin))

        if self.playing and self.pdrag \
                and frame + self.trk.begin == self.trk.end:
            frame -= 1

        self.trk.seek(frame + self.trk.begin)

        # If music mode is active, load the sample for the selected region.
        if self.k.music.active and self.music_mode_override:
            self.k.music.seek_by_frame(self.trk.frame)

        self.update_frame(frame)

        if self.playing and not self.pdrag and self.holding:
            self.op_seek()

    def update_frame(self, frame):
        self.progress.set_current_value(frame)
        self.lbl_frame.set_text(str(frame))

    def tick(self):
        if self.playing is not None:
            pframe = round(self.progress.get_current_value())

            if pframe != self.trk.frame - self.trk.begin:
                #print(f'seeking pframe {pframe}')
                self.seek(pframe)

            elif self.hold_loop_override and self.playing and not self.pdrag:
                if pframe < self.hold_loop_begin or pframe > self.hold_loop_end:
                    self.seek(self.hold_loop_begin)

            elif self.music_mode_override and self.playing and not self.pdrag and not self.holding:
                if pframe < self.music_mode_loop_begin or pframe > self.music_mode_loop_end:
                    self.seek(self.music_mode_loop_begin)

            elif self.playing and self.pdrag:
                self.seek(self.trk.frame - self.trk.begin - 1)

            #elif self.holding < 0:
            #    self.seek(self.flast)

            elif self.holding:
                if len(self.holding) > 1:
                    self.seek(self.flast)

                    for key in self.holding:
                        self.keydown(key, MOD_MAN)

                elif self.holding[0] == pygame.K_KP_PERIOD:
                    self.seek(self.flast)

            elif self.loop and (pframe < self.loop_begin \
                    or pframe > self.loop_end):
                #if self.holding == 0:
                if not self.holding:
                    self.seek(self.loop_begin)

            tock = self.trk.tick()

            if tock is None:
                self.stop()

            elif tock is not False:
                self.img = tock
                self.update_frame(self.trk.frame - self.trk.begin)

        self.paint()

    def paint(self):
        if not self.k.player.big and not self.k.ack:
            self.paint_loop_bar()

        if self.playing is None:
            if self.thumb is not None:
                self.paint_thumb()
        else:
            self.paint_video()

    def paint_thumb(self):
        self.paint_image(self.thumb, self.thumb.get_width(),
            self.thumb.get_height())

    def paint_video(self):
        self.paint_image(self.img, self.trk.size[0], self.trk.size[1])

    def paint_image(self, img, w, h):
        if self.k.player.big:
            x = int((WIDTH - w) / 2)
            y = int((HEIGHT - STATUS - h) / 2)
        else:
            x = PRECT[0]
            y = PRECT[1]

        if img is True:
            self.trk.res.ie.speed(self.trk.res, self.trk.frame, (x, y), (w, h))
        else:
            self.k.blit(img, (x, y))

    def paint_loop_bar(self):
        self.k.blit(self.loop_bar, (PRECT[0], VPRECT[3]))

    def draw_loop_bar(self):
        self.loop_bar.fill(BLACK)
        color = RED if self.loop else GREEN
        width = PWIDTH-65
        x_begin = round(width * self.loop_begin / self.trk.frames)
        x_end = round(width * (1+self.loop_end) / self.trk.frames)

        if x_begin > width-3:
            x_begin = width-3
        if x_end - x_begin < 3:
            x_end = x_begin+3

        pygame.draw.rect(self.loop_bar, color,
            pygame.Rect((32+x_begin, 0), (x_end-x_begin, 3)))

    def size_to_fit(self, width, height):
        self.trk.size_to_fit(width, height)

        bg = pygame.Surface((width, height))
        bg.fill((9, 81, 18))

        if self.thumb_orig:
            size = get_size_to_fit(self.thumb_orig.get_size(), (width, height))
            self.thumb = pygame.transform.smoothscale(self.thumb_orig, size)
            tw = self.thumb.get_width()
            th = self.thumb.get_height()
            if tw < width or th < height:
                x = int((width - tw) / 2)
                y = int((height - th) / 2)
                bg.blit(self.thumb, (x, y))
                self.thumb = bg
        else:
            self.thumb = bg

    def panel_swap(self, btn, panel):
        if btn is self.panel_chaos and self.cur_panel is self.panel_chaos:
            self.cur_panel.show()

        super().panel_swap(btn, panel, self.cur_panel is not self.panel_chaos)

    def click(self, element, target=None):
        if element is self.btn_pp:
            self.pause() if self.playing else self.play()
            if self.k.f_key_capturing:
                from k.player.actions import PlayerPlay, PlayerPause
                # The action is recorded based on the new state
                if self.playing:
                    frag_id = getattr(self, 'frag_id', None)
                    if frag_id is not None:
                         self.k.f_key_current_actions.append(PlayerPlay(frag_id))
                else:
                    self.k.f_key_current_actions.append(PlayerPause())

        elif element is self.btn_save:
            self.k.job(self.save)

        elif element is self.btn_clip:
            # Note: clip/seq actions are not currently recorded for loops
            self.k.job(self.clip)

        elif element is self.btn_seq:
            self.k.job(self.seq)

        elif element is self.btn_chaos:
            self.panel_swap(self.btn_chaos, self.panel_chaos)

        else:
            return self.cur_panel.click(element, target)

        return True

    def mouse_down(self, event):
        if self.playing is None:
            return

        if event.button != pygame.BUTTON_LEFT:
            return

        pos = event.pos
        prect = self.progress.get_relative_rect()
        srect = self.progress.sliding_button.get_relative_rect()
        bw = self.progress.arrow_button_width

        if pos[0] > PRECT[0] + prect[0] + bw \
                and pos[0] < PRECT[0] + prect[0] + prect[2] - bw \
                and pos[1] > PRECT[1] + prect[1] \
                and pos[1] < PRECT[1] + prect[1] + prect[3]:

            self.pdrag = True
            self.op_hold()

            if not (pos[0] >= PRECT[0] + srect[0] \
                    and pos[0] <= PRECT[0] + srect[0] + srect[2]):

                x = pos[0] - PRECT[0] - bw
                w = prect[2] - 2*bw
                f = int((x / w) * self.trk.frames)

                self.seek(f)

    def mouse_up(self, event):
        if event.button != pygame.BUTTON_LEFT:
            return

        self.pdrag = False

        if self.playing:
            self.op_seek()

    def keydown(self, key, mod):
        #print(f'{self.holding} DOWN {key}')
        pygame.key.set_repeat(0)

        man = False
        alt = False
        ctrl = False
        shift = False

        if mod == MOD_MAN:
            man = True

        else:
            alt = mod & pygame.KMOD_ALT
            ctrl = mod & pygame.KMOD_CTRL
            shift = mod & pygame.KMOD_SHIFT or mod & pygame.KMOD_LSHIFT \
                or mod & pygame.KMOD_RSHIFT

        nomod = not alt and not ctrl and not shift

        if nomod:
            if key == pygame.K_SPACE:
                # Save current selection to next available slot, looping around when full.
                slot_key = self.selection_slot_order[self.next_selection_slot_index]

                self.selection_regions[slot_key] = (self.loop_begin, self.loop_end)
                print(f"Selection saved to slot {self.selection_key_map.get(slot_key, slot_key)}")

                # If music mode is active, cache the audio for this new slot
                if self.k.music.active:
                    self.k.music.cache_sample_for_slot(slot_key, self)

                self.next_selection_slot_index = (self.next_selection_slot_index + 1) % len(self.selection_slot_order)

                return  # event handled

            elif key in self.selection_slot_order:
                # If music mode is active, load the sample instead of swapping regions.
                if self.k.music.active:
                    if key in self.selection_regions:
                        self.k.music.load_slotted_sample(key)
                    else:
                        print(f"No selection in slot {self.selection_key_map.get(key, key)}")

                # Hold-to-loop on saved selection region, regardless of music mode.
                if not man and key not in self.holding:
                    if key in self.selection_regions:
                        self.hold_loop_override = True
                        self.hold_loop_key = key
                        self.hold_loop_begin, self.hold_loop_end = self.selection_regions[key]

                        if self.playing in [None, False]:
                            self.play()

                        self.seek(self.hold_loop_begin)
                        self.keyhold(key)  # Use existing hold mechanism to track key release
                    else:
                        # Only print if not in music mode, as it's already handled above if active.
                        if not self.k.music.active:
                            print(f"No selection in slot {self.selection_key_map.get(key, key)}")
                return  # event handled
            elif key == pygame.K_BACKQUOTE:
                # Load from default slot, swapping with current.
                if pygame.K_BACKQUOTE in self.selection_regions:
                    current_selection = (self.loop_begin, self.loop_end)
                    self.loop_begin, self.loop_end = self.selection_regions[pygame.K_BACKQUOTE]
                    self.selection_regions[pygame.K_BACKQUOTE] = current_selection
                    print(f"Swapped current selection with default slot `")
                    self.draw_loop_bar()
                else:
                    print("No selection in default slot `")
                return  # event handled

        if key == pygame.K_KP_ENTER:
            if self.playing:
                self.pause()
            else:
                self.play()

        elif key == pygame.K_HOME:
            self.stop()
            self.play()

        elif key == pygame.K_END:
            self.stop()

        elif key == pygame.K_UP:
            if not man:
                self.keyhold(key)

            if self.playing:
                if nomod:
                    self.seek(self.trk.frame + PLAY_SEEK_VERT)
                elif ctrl:
                    self.seek(self.trk.frame + PLAY_SEEK_VERT_CTRL)
                elif shift:
                    self.seek(self.trk.frame + PLAY_SEEK_VERT_SHIFT)
            else:
                if nomod:
                    self.seek(self.trk.frame + PAUSE_SEEK_VERT)
                elif ctrl:
                    self.seek(self.trk.frame + PAUSE_SEEK_VERT_CTRL)
                elif shift:
                    self.seek(self.trk.frame + PAUSE_SEEK_VERT_SHIFT)

        elif key == pygame.K_DOWN:
            if not man:
                self.keyhold(key)

            if self.playing:
                if nomod:
                    self.seek(self.trk.frame - PLAY_SEEK_VERT)
                elif ctrl:
                    self.seek(self.trk.frame - PLAY_SEEK_VERT_CTRL)
                elif shift:
                    self.seek(self.trk.frame - PLAY_SEEK_VERT_SHIFT)
            else:
                if nomod:
                    self.seek(self.trk.frame - PAUSE_SEEK_VERT)
                elif ctrl:
                    self.seek(self.trk.frame - PAUSE_SEEK_VERT_CTRL)
                elif shift:
                    self.seek(self.trk.frame - PAUSE_SEEK_VERT_SHIFT)

        elif key == pygame.K_LEFT:
            if not man:
                self.keyhold(key)

            if nomod:
                self.seek(self.trk.frame - SEEK_HORIZ)
            elif ctrl:
                self.seek(self.trk.frame - SEEK_HORIZ_CTRL)
            elif shift:
                self.seek(self.trk.frame - SEEK_HORIZ_SHIFT)

        elif key == pygame.K_RIGHT:
            if not man:
                self.keyhold(key)

            if nomod:
                self.seek(self.trk.frame + SEEK_HORIZ)
            elif ctrl:
                self.seek(self.trk.frame + SEEK_HORIZ_CTRL)
            elif shift:
                self.seek(self.trk.frame + SEEK_HORIZ_SHIFT)

        elif key == pygame.K_KP0:
            if nomod:
                if not man:
                    self.keyhold(key, True)

                if self.loop:
                    self.seek(0)
                else:
                    self.seek(self.loop_begin)

        elif key >= pygame.K_KP1 and key <= pygame.K_KP9:
            if nomod:
                if not man:
                    self.keyhold(key, True)
                self.seek(self.jumps[key - pygame.K_KP1])
            elif ctrl and not man:
                idx = key - pygame.K_KP1
                frame = self.trk.frame - self.trk.begin
                self.jumps[idx] = frame
                self.lbl_jumps[idx].set_relative_position(
                    (28 + int((PWIDTH-65) * frame / self.trk.frames),
                    295))

        elif key == pygame.K_KP_PERIOD:
            if self.playing:
                #if self.holding == 0 or self.holding is None:
                #    self.op_hold()
                #    self.flast = self.trk.frame
                #    self.holding = -1 * key
                #elif self.holding > 0:
                #    self.op_hold()
                #    self.holding = -1 * self.holding
                #else:
                #    #print('how did this happen (key already down)?')
                #    pass
                if man:
                    self.seek(self.flast)
                else:
                    self.keyhold(key, True)
                    #self.holding.append(key)

        elif key == pygame.K_KP_DIVIDE:
            if nomod:
                self.loop_begin = self.trk.frame - self.trk.begin
                if self.loop_begin > self.loop_end:
                    self.loop_end = self.trk.end - self.trk.begin
                self.draw_loop_bar()
                #if self.btn_save:
                #    self.btn_save.enable()

        elif key == pygame.K_KP_MULTIPLY:
            if nomod:
                self.loop_end = self.trk.frame - self.trk.begin
                if self.loop_end < self.loop_begin:
                    self.loop_begin = 0
                self.draw_loop_bar()
                #if self.btn_save:
                #    self.btn_save.enable()

        elif key == pygame.K_KP_PLUS:
            if nomod:
                if not self.loop:
                    self.loop = True
                    self.draw_loop_bar()
                    #if self.btn_save:
                    #    self.btn_save.enable()

                #self.keyhold(key)
                self.seek(self.loop_begin)

        elif key == pygame.K_KP_MINUS:
            if nomod:
                if self.loop:
                    self.loop = False
                    self.draw_loop_bar()
                    #if self.btn_save:
                    #    self.btn_save.enable()

                if not man:
                    self.keyhold(key)

                self.seek(self.loop_end)

    def keyup(self, key, mod):
        #print(f'{self.holding} UP {key}')

        if self.hold_loop_override and key == self.hold_loop_key:
            self.hold_loop_override = False
            self.hold_loop_key = None

        if key == pygame.K_ESCAPE:
            self.k.player.killall()
            return

        #if self.holding < 0:
        #    self.holding = -1 * self.holding

        #    if self.holding == key:
        #        self.holding = 0

        #    self.op_unhold()

        #elif self.holding == 0:
        #    if key == pygame.K_KP0:
        #        self.seek(self.loop_begin)
        #    elif key >= pygame.K_KP1 and key <= pygame.K_KP9:
        #        self.seek(self.jumps[key - pygame.K_KP1])

        #else:
        #    self.holding = 0

        while key in self.holding:
            idx = self.holding.index(key)
            del self.holding[idx]

            if idx > 0:
                if self.loop and key == pygame.K_KP_PERIOD:
                    self.seek(self.flast)
                else:
                    self.keydown(self.holding[idx-1], MOD_MAN)

    def keyhold(self, key, magic=False):
        #if self.holding < 0:
        #    self.holding = -1 * key
        #elif magic and self.holding == 0:
        #    self.flast = self.trk.frame - self.trk.begin
        #    self.holding = key
        #elif magic and (self.holding >= pygame.K_KP1 \
        #        and self.holding <= pygame.K_KP9) \
        #        or self.holding == pygame.K_KP0:
        #    self.holding = -1 * self.holding
        #else:
        #    self.holding = key

        if magic or not self.holding:
            self.flast = self.trk.frame - self.trk.begin

        self.holding.append(key)

    def op_start(self):
        #self.k.replay_op(self.trk.res.video_id, kdb.OP_START,
        #    self.trk.frame + self.trk.begin)
        pass

    def op_stop(self):
        #self.k.replay_op(self.trk.res.video_id, kdb.OP_STOP,
        #    self.trk.frame + self.trk.begin)
        pass

    def op_seek(self):
        self.op_start()

    def op_hold(self):
        #self.k.replay_op(self.trk.res.video_id, kdb.OP_HOLD,
        #    self.trk.frame + self.trk.begin)
        pass

    def op_unhold(self):
        self.op_start()


class Chaos(KPanel):
    def __init__(self, p):
        super().__init__(p.k, None, p.container, PRACK, 1)

        self.btn_chaos = p.btn_chaos

        self.btn_loop = pygame_gui.elements.UIButton(
            text='Loop',
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((0, 0), (100, 25)))

        self.btn_select = pygame_gui.elements.UIButton(
            text='Select',
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((110, 0), (100, 25)))

        self.btn_jumps = pygame_gui.elements.UIButton(
            text='Decimate',
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((220, 0), (100, 25)))

        images = media.list_ack_images()
        if images:
            yesser = random.randint(0, 1)
            image = images[random.randint(0, len(images)-1)]
            while yesser and image and image.endswith('_combined'):
                del images[images.index(image)]
                if images:
                    image = images[random.randint(0, len(images)-1)]
                else:
                    image = None
            if image: image = media.get_ack_image(image)
            surf = pygame.Surface(image.get_size(), flags=pygame.SRCALPHA)
            surf.blit(IMAGE, (0, 0))
            rimages = media.list_replay_images()
            if rimages and yesser:
                rimage = rimages[random.randint(0, len(rimages)-1)]
                rimages = media.list_replay_images(rimage)
                if rimages:
                    surf.blit(media.get_replay_image(rimage,
                        rimages[random.randint(0, len(rimages)-1)]), (81, 42))
            if image: surf.blit(image, (0, 0))
            surf.blit(media.get_ack_image(
                images[random.randint(0, len(images)-1)]), (9, 18))
            image = surf
        else:
            image = IMAGE

        self.image = pygame_gui.elements.UIImage(
            image_surface=image,
            manager=self.k.gui,
            container=self.container,
            relative_rect=CRACK)

        self.image = image if image is not IMAGE else None

        self.cur_btn = self.btn_chaos
        self.cur_panel = self.image

    def show(self):
        if self.cur_btn is not self.btn_chaos:
            self.cur_btn.enable()
        self.cur_btn = self.btn_chaos
        if self.cur_panel is not self.image:
            self.cur_panel.kill()
            self.cur_panel = self.image

        super().show()

    def panel_swap(self, btn, panel):
        super().panel_swap(btn, panel, self.cur_panel is not self.image)

    def click(self, element, target=None):
        if element is self.btn_loop:
            self.k.job(self.click_loop)

        elif element is self.btn_select:
            self.k.job(self.click_select)

        elif element is self.btn_jumps:
            self.k.job(self.click_jumps)

        else:
            return False

        return True

    def click_loop(self):
        self.panel_swap(self.btn_loop, Loop(self))

    def click_select(self):
        self.panel_swap(self.btn_select, Select(self))

    def click_jumps(self):
        self.panel_swap(self.btn_jumps, Jumps(self))


class Loop(KPanel):
    def __init__(self, p):
        super().__init__(p.k, None, p.container, CRACK, 1)

        self.lbl = pygame_gui.elements.UILabel(
            text='loop',
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((0, 0), (-1, -1)))


class Select(KPanel):
    def __init__(self, p):
        super().__init__(p.k, None, p.container, CRACK, 1)

        self.lbl = pygame_gui.elements.UILabel(
            text='select',
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((0, 0), (-1, -1)))


class Jumps(KPanel):
    def __init__(self, p):
        super().__init__(p.k, None, p.container, CRACK, 1)

        self.lbl = pygame_gui.elements.UILabel(
            text='decimate',
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((0, 0), (-1, -1)))