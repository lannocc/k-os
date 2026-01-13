from k.ui import *
import k.db as kdb
import k.storage as media
from k.home import IMAGE
from k.replay.ops import Action
from k.player.actions import *
from .core import get_size_to_fit

import random
import time
import json


PRECT = pygame.Rect((WIDTH-PWIDTH, 0), (PWIDTH, HEIGHT))
VPRECT = pygame.Rect((PRECT[0], PRECT[1]), (PRECT[2], 313))
PRACK = pygame.Rect((140, 370), (PWIDTH-150, HEIGHT-STATUS-380))
CRACK = pygame.Rect((0, 35), (PRACK[2], PRACK[3]-35))

MOD_MAN = 666


class Player(KPanel):
    def __init__(self, k, tracker, thumbnail=None, loop=None, jumps=None, selection_regions_json=None, frag_id=None):
        super().__init__(k, relative_rect=PRECT, visible=1)

        self.frag_id = frag_id
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
            button_text = "Save" if self.frag_id else "Save*"
            self.btn_save = pygame_gui.elements.UIButton(
                text=button_text,
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
        if selection_regions_json:
            try:
                loaded_regions = json.loads(selection_regions_json)
                self.selection_regions = {int(k): v for k, v in loaded_regions.items()}
            except (json.JSONDecodeError, TypeError):
                print("Warning: Could not load corrupt selection regions data.")
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
        self._set_initial_selection_slot_index()

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

        self.playback_direction = 1
        self.playback_speed = 1.0

        # For temporary fast-forward/rewind
        self.ff_rew_keys_down = 0
        self.original_playback_direction = 1
        self.original_playback_speed = 1.0

        # For music mode override
        self.music_mode_override = False
        self.music_mode_loop_begin = 0
        self.music_mode_loop_end = 0

        # For hold-to-loop override on number keys
        self.hold_loop_override = False
        self.hold_loop_key = None
        self.hold_loop_begin = 0
        self.hold_loop_end = 0

        # Volume control
        self.volume = 1.0
        self.volume_change_rate = 1.0 / 5.0  # Full range in 5 seconds
        self.volume_direction = 0  # -1 for down, 0 for none, 1 for up
        self._last_vol_update_time = 0

        self.reset()

    def reset(self):
        self.progress.disable()
        self.progress.set_current_value(0)
        self.btn_pp.set_text('PLAY')
        self.lbl_frame.set_text(f'[{self.trk.frames}]')

        #self.holding = 0
        self.holding = [ ]
        self.pdrag = False

        self.ff_rew_keys_down = 0

        self.music_mode_override = False
        self.hold_loop_override = False
        self.hold_loop_key = None
        self.playback_direction = 1
        if hasattr(self.trk, 'set_direction'):
            self.trk.set_direction(1)
        self.playback_speed = 1.0
        if hasattr(self.trk, 'set_speed'):
            self.trk.set_speed(1.0)

        self.volume = 1.0
        if hasattr(self.trk, 'res') and hasattr(self.trk.res, 'audio'):
            self.trk.res.audio.set_volume(self.volume)

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
            # On play, ensure current volume is applied, but don't reset to 1.0 unless it's a new clip
            if not self.k.music.active:
                 self.trk.res.audio.set_volume(self.volume)
        self.music_mode_override = False

        self.trk.play()
        self.playing = True

    def pause(self):
        if not self.playing:
            return

        if self.k.f_key_capturing:
            self.k.f_key_current_actions.append(PlayerPause())

        self.op_stop()
        self.btn_pp.set_text('RESUME')

        self.trk.pause()
        self.playing = False

    def stop(self, replace=False):
        if self.playing is None:
            return

        if self.k.f_key_capturing:
            self.k.f_key_current_actions.append(PlayerStop())

        self.reset()

        if not replace:
            self.op_stop()
            self.k.replay_break()

    def seek(self, frame):
        self.k.flash_player_indicator()

        if self.k.f_key_capturing:
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
        # Handle shift-key override for save button text
        if self.btn_save and self.frag_id:
            keys = pygame.key.get_pressed()
            is_shift_pressed = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
            if is_shift_pressed:
                if self.btn_save.text != "Save*":
                    self.btn_save.set_text("Save*")
            else:
                if self.btn_save.text != "Save":
                    self.btn_save.set_text("Save")

        if self.volume_direction != 0:
            now = time.perf_counter()
            if self._last_vol_update_time == 0:
                self._last_vol_update_time = now

            tdelta = now - self._last_vol_update_time
            self._last_vol_update_time = now

            change = self.volume_direction * self.volume_change_rate * tdelta
            new_volume = max(0.0, min(1.0, self.volume + change))
            if new_volume != self.volume:
                self.volume = new_volume
                if self.k.f_key_capturing:
                    self.k.f_key_current_actions.append(PlayerSetVolume(self.volume))
                if hasattr(self.trk, 'res') and hasattr(self.trk.res, 'audio'):
                    if not self.k.music.active or not self.k.music.active_notes:
                        self.trk.res.audio.set_volume(self.volume)
        else:
            self._last_vol_update_time = 0

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
                    if self.playback_direction == 1:
                        self.seek(self.loop_begin)
                    else:
                        self.seek(self.loop_end)

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

    def set_playback_speed(self, speed, direction=None):
        if direction is None:
            direction = self.playback_direction

        if self.playback_speed == speed and self.playback_direction == direction:
            return

        if self.k.f_key_capturing:
            self.k.f_key_current_actions.append(PlayerSetSpeed(speed, direction))

        self.playback_speed = speed
        self.playback_direction = direction

        if hasattr(self.trk, 'set_speed'):
            self.trk.set_speed(self.playback_speed)
        if hasattr(self.trk, 'set_direction'):
            self.trk.set_direction(self.playback_direction)

    def toggle_playback_direction(self):
        self.set_playback_speed(self.playback_speed, -self.playback_direction)

    def keydown(self, key, mod, keys_down=None):
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

        # Adjust individual track/sample volume
        if (key == pygame.K_PAGEUP or key == pygame.K_PAGEDOWN) and keys_down is not None:
            volume_change = 0.1 if key == pygame.K_PAGEUP else -0.1
            key_handled = False

            # Check for held F-key
            f_keys = [pygame.K_F1 + i for i in range(12)]
            held_f_key = next((k for k in keys_down if k in f_keys and k != key), None)

            if held_f_key and held_f_key in self.k.f_key_loops:
                loop_data = self.k.f_key_loops[held_f_key]
                current_volume = float(loop_data.get('volume', 1.0))
                new_volume = round(max(0.0, min(1.0, current_volume + volume_change)), 2)
                loop_data['volume'] = new_volume

                if held_f_key in self.k.player.loop_players:
                    self.k.player.loop_players[held_f_key].set_volume(new_volume)

                print(f"Track {pygame.key.name(held_f_key).upper()} volume set to {new_volume:.2f}")
                self.k.status()
                key_handled = True

            # If not an F-key, check if we're in music mode and should adjust the active sample's volume
            if not key_handled and self.k.music.active:
                active_slot_key = self.k.music.active_slot_key
                if active_slot_key and active_slot_key in self.selection_regions:
                    # A note or sample key must be held to prevent adjusting volume just by holding pageup/down
                    is_music_related_key_held = any(k in self.k.music.music_keys for k in keys_down if k != key)

                    if is_music_related_key_held:
                        region_data = self.selection_regions[active_slot_key]
                        region = list(region_data)
                        while len(region) < 3: region.append(1.0)  # Default volume

                        current_volume = float(region[2])
                        new_volume = round(max(0.0, min(1.0, current_volume + volume_change)), 2)
                        region[2] = new_volume
                        self.selection_regions[active_slot_key] = tuple(region)

                        clip_id = self.get_or_create_frag_id()
                        if clip_id is not None:
                            kdb.set_clip_selection_regions(clip_id, json.dumps(self.selection_regions))

                        # Update the live music mode volume
                        if self.k.f_key_capturing:
                            self.k.f_key_current_actions.append(PlayerSetMusicVolume(new_volume))
                        self.k.music.volume = new_volume
                        self.k.music.update_active_note_volume()

                        slot_name = self.selection_key_map.get(active_slot_key, 'current')
                        print(f"Sample slot {slot_name} volume set to {new_volume:.2f}")
                        self.k.status()
                        key_handled = True

            if key_handled:
                return  # Event fully handled, prevents main volume change

        if ctrl and not shift and not alt:
            if key in self.selection_slot_order:
                if key in self.selection_regions:
                    region = list(self.selection_regions[key])
                    # Ensure region data has 4 elements (loop_begin, loop_end, volume, locked)
                    while len(region) < 4:
                        region.append(False)  # Add default values if missing
                    was_locked = region[3]
                    region[3] = not was_locked  # Toggle locked state
                    self.selection_regions[key] = tuple(region)
                    state = "locked" if region[3] else "unlocked"
                    print(f"Sample slot {self.selection_key_map.get(key, key)} is now {state}.")

                    clip_id = self.get_or_create_frag_id()
                    if clip_id is not None:
                        kdb.set_clip_selection_regions(clip_id, json.dumps(self.selection_regions))

                    if was_locked: # Just unlocked it
                        # If all other slots are locked, this becomes the new target
                        all_others_locked = True
                        for other_key in self.selection_slot_order:
                            if other_key == key: continue
                            other_region = self.selection_regions.get(other_key)
                            if not (other_region and len(other_region) > 3 and other_region[3]):
                                all_others_locked = False
                                break
                        if all_others_locked:
                            self.next_selection_slot_index = self.selection_slot_order.index(key)
                            print(f"Only available slot {self.selection_key_map.get(key, key)} is now the target.")
                    else: # Just locked it
                        # If the currently targeted slot was just locked, find a new target.
                        if self.selection_slot_order[self.next_selection_slot_index] == key:
                            self._find_next_unlocked_slot()
                else:
                    print(f"No selection in slot {self.selection_key_map.get(key, key)} to lock.")
                return True

        nomod = not alt and not ctrl and not shift

        if nomod and key == pygame.K_SLASH:
            self.toggle_playback_direction()
            return

        if nomod and (key == pygame.K_PERIOD or key == pygame.K_COMMA):
            if self.ff_rew_keys_down == 0:
                self.original_playback_direction = self.playback_direction
                self.original_playback_speed = self.playback_speed
            self.ff_rew_keys_down += 1

            if key == pygame.K_PERIOD:
                if self.playback_direction == 1:
                    self.set_playback_speed(2.0, 1)
                else:  # direction is -1
                    self.set_playback_speed(1.0, 1)
            else:  # key == pygame.K_COMMA
                if self.playback_direction == -1:
                    self.set_playback_speed(2.0, -1)
                else:  # direction is 1
                    self.set_playback_speed(1.0, -1)
            return

        if nomod:
            if key == pygame.K_SPACE:
                # Save current selection to next available slot, looping around when full.
                slot_key = self.selection_slot_order[self.next_selection_slot_index]

                region_data = self.selection_regions.get(slot_key)
                if region_data and len(region_data) > 3 and region_data[3]:
                    print(f"Cannot save: Target slot {self.selection_key_map.get(slot_key, slot_key)} is locked.")
                    return True  # event handled

                self.selection_regions[slot_key] = (self.loop_begin, self.loop_end, self.volume, False)
                print(f"Selection saved to slot {self.selection_key_map.get(slot_key, slot_key)}")

                clip_id = self.get_or_create_frag_id()
                if clip_id is not None:
                    kdb.set_clip_selection_regions(clip_id, json.dumps(self.selection_regions))

                # If music mode is active, cache the audio for this new slot
                if self.k.music.active:
                    self.k.music.cache_sample_for_slot(slot_key, self)

                self._find_next_unlocked_slot()

                return True  # event handled

            elif key in self.selection_slot_order:
                # In non-music mode, number keys activate hold-to-loop on a saved region.
                # In music mode, this event is handled by k.player.music and this code is not reached.
                if not man and key not in self.holding:
                    if key in self.selection_regions:
                        self.hold_loop_override = True
                        self.hold_loop_key = key
                        self.hold_loop_begin, self.hold_loop_end, *_ = self.selection_regions[key]

                        if self.playing in [None, False]:
                            self.play()

                        self.seek(self.hold_loop_begin)
                        self.keyhold(key)  # Use existing hold mechanism to track key release
                    else:
                        print(f"No selection in slot {self.selection_key_map.get(key, key)}")
                return  # event handled
            elif key == pygame.K_BACKQUOTE:
                # Load from default slot, swapping with current.
                if pygame.K_BACKQUOTE in self.selection_regions:
                    current_selection = (self.loop_begin, self.loop_end, self.volume)
                    self.loop_begin, self.loop_end, self.volume = self.selection_regions[pygame.K_BACKQUOTE]
                    self.selection_regions[pygame.K_BACKQUOTE] = current_selection
                    print(f"Swapped current selection with default slot `")
                    self.draw_loop_bar()
                else:
                    print("No selection in default slot `")
                return  # event handled

        if key == pygame.K_PAGEUP:
            self.volume_direction = 1
            return
        elif key == pygame.K_PAGEDOWN:
            self.volume_direction = -1
            return

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
        if key == pygame.K_BACKSPACE:
            # This handler is called after the OS-level backspace keyup handler.
            # The k.backspace_action_taken flag is shared state.
            if not self.k.backspace_action_taken:
                nomod = not (mod & pygame.KMOD_ALT or mod & pygame.KMOD_CTRL or mod & pygame.KMOD_SHIFT)
                if nomod:
                    self._find_previous_unlocked_slot()
            return

        if key == pygame.K_PAGEUP and self.volume_direction == 1:
            self.volume_direction = 0
        elif key == pygame.K_PAGEDOWN and self.volume_direction == -1:
            self.volume_direction = 0

        if key == pygame.K_PERIOD or key == pygame.K_COMMA:
            if self.ff_rew_keys_down > 0:
                self.ff_rew_keys_down -= 1
            if self.ff_rew_keys_down == 0:
                self.set_playback_speed(self.original_playback_speed, self.original_playback_direction)
            return

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

    def _set_initial_selection_slot_index(self):
        """Sets the initial next_selection_slot_index based on existing regions."""
        # a) First look for a completely unused slot.
        for i, key in enumerate(self.selection_slot_order):
            if key not in self.selection_regions:
                self.next_selection_slot_index = i
                return

        # b) If all slots are used, look for the first unlocked slot.
        for i, key in enumerate(self.selection_slot_order):
            region_data = self.selection_regions.get(key)
            is_locked = region_data and len(region_data) > 3 and region_data[3]
            if not is_locked:
                self.next_selection_slot_index = i
                return
        
        # If all slots are used and locked, default to 0. The save handler will handle it.
        self.next_selection_slot_index = 0

    def _find_previous_unlocked_slot(self):
        """Finds the previous available (unlocked) selection slot and updates self.next_selection_slot_index."""
        num_slots = len(self.selection_slot_order)

        # Start searching from the slot *before* the current one.
        for i in range(num_slots):
            check_index = (self.next_selection_slot_index - 1 - i + num_slots) % num_slots
            slot_key = self.selection_slot_order[check_index]

            region_data = self.selection_regions.get(slot_key)
            is_locked = region_data and len(region_data) > 3 and region_data[3]

            if not is_locked:
                self.next_selection_slot_index = check_index
                return

    def _find_next_unlocked_slot(self):
        """Finds the next available (unlocked) selection slot and updates self.next_selection_slot_index."""
        num_slots = len(self.selection_slot_order)
        
        # Start searching from the slot *after* the current one.
        for i in range(num_slots):
            check_index = (self.next_selection_slot_index + 1 + i) % num_slots
            slot_key = self.selection_slot_order[check_index]
            
            region_data = self.selection_regions.get(slot_key)
            is_locked = region_data and len(region_data) > 3 and region_data[3]
            
            if not is_locked:
                self.next_selection_slot_index = check_index
                return
        
        # If we get here, all slots are locked. The index doesn't change.
        # The K_SPACE handler will see the target is locked and fail gracefully.


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
