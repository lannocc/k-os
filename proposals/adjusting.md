# Advanced Adjustments and Workflow Enhancements

**Status:** Partially Implemented (all except for section 2)

This document proposes a set of features aimed at providing more fine-grained, interactive control over captured F-key loop tracks and music samples. It also includes several quality-of-life improvements to streamline the creative workflow, such as track/sample copying and quick region swapping.

## 1. Boundary Adjustments for Selections, Tracks, and Samples

### A. Summary

Users need a quick, interactive way to adjust the start and end points of their creations without having to recapture them entirely. This proposal introduces a unified keybinding system using the `+` and `-` keys to adjust the boundaries of the main player's selection region, an F-key loop's duration, or a music sample's region.

-   **Keys:** `+` (`=`) moves a boundary to the right; `-` (`_`) moves it to the left.
-   **Modifier:** `Shift` adjusts the start point; no modifier adjusts the end point.
-   **Interaction:** A single key press adjusts by one frame. Holding the key down will cause the adjustment rate to accelerate.

### B. Implementation Plan (`k/player/ui.py`)

1.  **New State Variables in `Player` Class:**
    *   Add variables to track the adjustment state, e.g., `self.adjusting_target = None`, `self.adjusting_boundary = 'end'`, `self.adjustment_direction = 0`, `self.adjustment_start_time = 0`.

2.  **Update `Player.keydown`:**
    *   Add a new block to handle `pygame.K_EQUALS` (`+`) and `pygame.K_MINUS` (`-`).
    *   Inside this block, determine the adjustment target:
        *   **F-Key Loop:** Check if an F-key is held down (using the `keys_down` set). If so, the target is the corresponding loop in `self.k.f_key_loops`.
        *   **Music Sample:** Check if a number key (0-9) is held down. If so, the target is the corresponding region in `self.selection_regions`.
        *   **Player Selection:** If neither is held, the target is the player's own `self.loop_begin` and `self.loop_end`.
    *   Check for the `Shift` modifier to set `self.adjusting_boundary` to `'start'` or `'end'`.
    *   Set `self.adjustment_direction` (`1` for `+`, `-1` for `-`) and `self.adjustment_start_time`.
    *   Perform the initial 1-frame adjustment.

3.  **Update `Player.tick`:**
    *   If `self.adjustment_direction` is not `0`, calculate the time held since `self.adjustment_start_time`.
    *   Based on the duration, determine an accelerated adjustment step size (e.g., 1 frame for <0.5s, 5 frames for <1.5s, 20 frames thereafter).
    *   Apply the adjustment to the appropriate target (`loop_begin`/`end`, F-key duration, or sample region boundary).

4.  **Persist Changes:**
    *   After each adjustment, call the relevant database function:
        *   For F-key loops, gather data and call `kdb.upsert_f_track`. Note that adjusting the duration of a music-based loop will require updating the `start_frame` or `end_frame` within its `music_context_json`.
        *   For music samples, call `kdb.set_clip_selection_regions` with the updated `self.selection_regions` dictionary.
    *   For player and sample adjustments, call `self.draw_loop_bar()` to update the UI. For F-key loops, call `self.k.status()` to redraw the status bar.

## 2. Advanced Loop/Sample Expansion Content

### A. Summary

When lengthening a track or sample, the default behavior will be to extend it with more of the original source audio. This proposal adds modifiers to allow for expansion with silence or reversed audio, enabling more creative sound design.

-   **With `}`/`]` key held:** Expand by inserting silence.
-   **With `{`/`[` key held:** Expand by inserting reversed audio from the source.

### B. Implementation Plan

This feature requires a fundamental change to how music contexts and selection regions are stored. They must evolve from a simple start/end pair to a list of segments.

1.  **Modify Data Structures:**
    *   The `music_context_json` for F-key tracks and the tuples in `selection_regions` for clips will no longer store just start/end frames. They will store a list of segment dictionaries, e.g., `[{'type': 'source', 'start': 100, 'end': 200}, {'type': 'silence', 'frames': 50}, {'type': 'reversed_source', 'start': 150, 'end': 100}]`.

2.  **Update Adjustment Logic (`k/player/ui.py`):**
    *   In the boundary adjustment logic from section 1, check if `pygame.K_RIGHTBRACKET` or `pygame.K_LEFTBRACKET` is held.
    *   If so, instead of modifying the `start`/`end` of an existing 'source' segment, append a new `'silence'` or `'reversed_source'` segment to the list.

3.  **Update Audio Caching/Playback:**
    *   **`k/player/music.py` (`cache_sample_for_slot`):** This method must be updated to read the new segment list. It will construct the final `AudioSegment` by iterating through the list, slicing/generating each part (`source`, `silent`, `reversed source`), and concatenating them before saving the cached `.wav` file.
    *   **`k/project/studio/__init__.py` (`cache_fkey_loop`):** This method will require the same logic as above to generate the cached `.wav` for F-key loops.
    *   **`k/player/loop.py` (`LoopPlayer`, `MicroMusicPlayer`):** When playing a loop that hasn't been cached (i.e., created live in a session), the `LoopPlayer` will need to perform the same audio-stitching logic in memory to create the `AudioSegment` for its `MicroMusicPlayer`.

## 3. Loop Synchronization Indicator

### A. Summary

To aid in creating rhythmically coherent loops, the F-key status indicator will provide visual feedback. When holding an F-key to adjust its track, the indicator will turn orange if its duration is a simple musical multiple or division of any other currently *playing* F-key loop.

### B. Implementation Plan (`k/K.py`)

1.  **Update `OS.status` Method:**
    *   Inside the `for i in range(self.TRACK_COUNT)` loop, check if the current `key` is in `self.keys_down`.
    *   If it is, this is the key being actively held/adjusted.
    *   Get its duration from `self.f_key_loops[key]['duration']`.
    *   Iterate through `self.player.loop_players.values()`. For each active `loop_player`, get its `duration`.
    *   Compare the two durations. A "match" occurs if `duration1 / duration2` (or its inverse) is close to a value in a predefined list of ratios (e.g., `[0.25, 0.333, 0.5, 1.0, 2.0, 3.0, 4.0]`).
    *   If a match is found, override the `color` variable for the indicator to `ORANGE` and break the inner loop. The existing drawing logic will then use this color.

## 4. Quick-Swap Selection Region

### A. Summary

The `~`/`` ` `` key will be repurposed to provide a fast way to audition a saved music sample's region in the main player. Pressing it swaps the player's current selection with the active music sample's region. Pressing it again swaps them back.

### B. Implementation Plan (`k/player/ui.py`)

1.  **Add State to `Player` Class:**
    *   Introduce a new member variable: `self.selection_buffer = None`.

2.  **Update `Player.keydown`:**
    *   Add a handler for `pygame.K_BACKQUOTE`.
    *   Check if `self.k.music.active_slot_key` is not `None`. If it is `None`, do nothing.
    *   **First Press (Swap In):** If `self.selection_buffer is None`:
        1.  Store the current player selection: `self.selection_buffer = (self.loop_begin, self.loop_end)`.
        2.  Get the region for the active sample from `self.selection_regions[self.k.music.active_slot_key]`.
        3.  Set `self.loop_begin` and `self.loop_end` from this region.
    *   **Second Press (Swap Back):** If `self.selection_buffer is not None`:
        1.  Set `self.loop_begin` and `self.loop_end` from `self.selection_buffer`.
        2.  Clear the buffer: `self.selection_buffer = None`.
    *   After the swap, call `self.draw_loop_bar()` to reflect the new selection.

## 5. Track and Sample Copying

### A. Summary

To speed up iteration, a simple key combination will allow copying F-key tracks and music samples from one slot to another.

-   **F-Key Track:** Hold `Alt` + `Source F-key` + `Target F-key`.
-   **Music Sample:** Hold `Alt` + `Source number key` + `Target number key`.

Copying into a locked slot will be disallowed.

### B. Implementation Plan

1.  **F-Key Track Copy (`k/K.py`)**
    *   In `OS.kick`, within the `KEYDOWN` handler, check if `Alt` is held (`event.mod & pygame.KMOD_ALT`).
    *   If an F-key is pressed, check `self.keys_down` for another F-key that is already held down.
    *   If found, identify the `source_key` (already held) and `target_key` (newly pressed).
    *   Check `self.f_key_loops.get(target_key, {}).get('locked', False)`. If `True`, print an error and return.
    *   Perform a deep copy of the source data: `self.f_key_loops[target_key] = copy.deepcopy(self.f_key_loops[source_key])`. Ensure the `'locked'` flag is `False` in the new copy.
    *   Call `kdb.upsert_f_track` to persist the new track data for `target_key`.
    *   Call `self.status()` to update the UI.

2.  **Music Sample Copy (`k/player/ui.py`)**
    *   In `Player.keydown`, add similar logic for number keys when `Alt` is held.
    *   Check `keys_down` for a `source_key` and identify the `target_key`.
    *   Check the locked status of the target region in `self.selection_regions`.
    *   If unlocked, copy the region data tuple: `self.selection_regions[target_key] = self.selection_regions[source_key]`.
    *   Call `kdb.set_clip_selection_regions` to persist the entire `selection_regions` dictionary.
    *   Trigger caching for the new slot: `self.k.music.cache_sample_for_slot(target_key, self)`.
    *   Call `self.k.status()` to update the UI.

