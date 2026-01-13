# K-OS Music Mode Implementation Plan

**Status:** Implemented

This document outlines a proposal for implementing a suite of music creation and performance features within the k-os application. The goal is to leverage the existing video clipping and playback engine to create a dynamic audio manipulation environment. The proposal is broken down into three main features.

## 1. F-Key Audio Loop Tracks

This feature introduces a live looping capability using the function keys (F1-F12), allowing for the creation of up to 12 simultaneous audio tracks.

### User Workflow

1.  **Recording a Loop:** The user holds down an F-key (e.g., `F1`). While the key is held, all audio-related actions performed in the main player (playing a clip, seeking, pausing) are recorded as a sequence.
2.  **Saving a Loop:** When the user releases the F-key, the recording stops, and the sequence is saved as a loop associated with that key.
3.  **Toggling Playback:** A short press of the same F-key (`F1`) toggles the playback of its associated loop. The loop will play from the beginning each time it's toggled on.
4.  **Layering:** The user can toggle multiple F-key loops simultaneously, allowing for the layering of audio tracks.

### Implementation Plan

1.  **Event Handling in `k/K.py`:**
    *   In the `OS.kick` method, add logic to detect `KEYDOWN` and `KEYUP` events for `pygame.K_F1` through `pygame.K_F12`.
    *   A simple timer mechanism will be used to differentiate between a short press (toggle) and a long press/hold (record). On `KEYDOWN`, a timer is started. If `KEYUP` occurs before a threshold (e.g., 500ms), it's a toggle; otherwise, it's a hold action.

2.  **Action Recording & Storage:**
    *   This will adapt the existing `k/replay` system for audio-only purposes.
    *   A new dictionary, `self.f_key_loops = {}`, will be added to the `OS` class to store the recorded action sequences for each F-key.
    *   On an F-key `KEYDOWN` hold, a new "recording" state is entered for that key. Player actions (play, pause, stop, seek) will be captured as `Action` objects (similar to `k/replay/ops.py`) and appended to a temporary list.
    *   On `KEYUP`, this list of actions is saved to `self.f_key_loops[event.key]`.

3.  **Simultaneous Playback Engine:**
    *   A new class, `k.player.Mixer`, will be created to act as the central manager for all audio sources.
    *   The `Mixer` will manage a dictionary of active `k.player.LoopPlayer` instances, one for each active F-key loop. These lightweight players consume recorded action lists to provide concurrent audio streams.
    *   Crucially, the `Mixer` will also contain the primary `k.player.Stack`. The `Stack` will continue to manage the main video and audio track that the user interacts with directly (e.g., via key-assigned clips). This architecture centralizes audio control while preserving the existing logic for stacking and replacing the main player.
    *   The `just_playback` library supports multiple `Playback()` instances, which makes this composite structure feasible.

4.  **Toggling Logic:**
    *   When a short press of an F-key is detected, the `OS` will call the `Mixer`.
    *   If a loop for that key is already playing, the `Mixer` will stop and destroy its player instance.
    *   If no loop is playing for that key and a recorded loop exists in `self.f_key_loops`, the `Mixer` will instantiate a new `LoopPlayer` with the recorded actions and start its playback.

## 2. Key-Assigned Clip Playback

This feature allows users to trigger video clips in the Project Studio using assigned keyboard keys, turning the clip library into a playable instrument.

### Current Status

This functionality is already partially implemented within the existing codebase.

*   **Assignment:** In the Project Studio's "Clip" panel (`k/project/studio/clip.py`), each clip has a "Key" input field. Entering a character (e.g., 'a') assigns that key to the clip.
*   **Triggering:** The `k/project/studio/__init__.py` file contains logic to handle `keydown` events. It maintains a dictionary `self.keys` mapping keycodes to clip `Entry` objects. When a registered key is pressed, it calls the `keydown` method on the corresponding clip `Entry`, which in turn calls its `play()` method.
*   **Stacking:** The clip's `play()` method has a `stack` parameter. Holding `Shift` while pressing the assigned key will stack the new player on top of the old one instead of replacing it.

### Proposed Action Plan

The existing implementation is sound and will be made permanently active. The concept of a separate "Performance Mode" toggle will be removed.

1.  **Enable by Default:** The `keydown` logic in `k/project/studio/__init__.py` will be reviewed, uncommented, and cleaned up to ensure it is always active. The `self.started` flag and any related UI toggles will be removed entirely. The UI will always remain fully interactive.
2.  **Input Priority:** The key triggers for clips will always be "hot" *unless* the global "Auto-Tune Music Mode" (Feature #3) is engaged. The main event loop in `OS.kick` will first check if `self.music_mode` is active; if it is, QWERTY input will be routed to the pitch-shifter. Otherwise, the event will be processed by the Project Studio for clip triggering.

## 3. Auto-Tune Music Mode

This feature introduces a global "Music Mode" that transforms a selected audio segment into a playable, pitched instrument using the QWERTY keyboard.

### User Workflow

1.  **Select Audio:** While a video is playing, the user can define a loop/selection.
2.  **Engage Music Mode:** The user presses the `Spacebar`. The application "captures" the audio from the current selection (or the entire clip if no selection is active).
3.  **Play Pitched Samples:** The QWERTY keyboard is now mapped to a musical scale. Pressing keys like 'a', 's', 'd' plays the captured audio sample at different pitches. The original key-assigned clip playback (Feature #2) is temporarily suspended.
4.  **Disengage:** The user presses the `Spacebar` again to exit Music Mode. The keyboard returns to its normal function. To capture a new sample, the user must exit and re-enter Music Mode.

### Implementation Plan

1.  **Global State and Toggle:**
    *   A new boolean flag, `self.music_mode`, will be added to the main `OS` class in `k/K.py`.
    *   In `OS.kick`, logic will be added to toggle this flag when `pygame.K_SPACE` is pressed and a player is active.

2.  **Audio Sample Capture:**
    *   When `self.music_mode` is toggled to `True`:
        *   The system will identify the active player and its associated `Tracker` (`self.k.player.players[-1].trk`).
        *   It will retrieve the source audio filename (`trk.res.afn`), the loop start/end points (`loop_begin`, `loop_end`), and the audio sample rate.
        *   A new dependency, such as **`pydub`**, will be required. This library will be used to load the audio file and slice the captured segment based on the start/end times.
        *   This sliced `AudioSegment` will be stored in a new `OS` property, `self.music_mode_sample`.

3.  **Real-time Pitch Shifting and Playback:**
    *   **Keyboard Mapping:** A dictionary will map QWERTY `pygame.K_*` constants to semitone shifts relative to the original sample's pitch. A standard piano-style layout will be used:
        *   **White Keys:** `a, s, d, f, g, h, j, k` (C, D, E, F, G, A, B, C')
        *   **Black Keys:** `w, e, t, y, u` (C#, D#, F#, G#, A#)
    *   **Event Handling:** The `OS.kick` method will be modified. If `self.music_mode` is `True`, it will intercept QWERTY key presses.
        *   The corresponding semitone shift will be looked up.
        *   Using the chosen audio library (e.g., `pydub`), a new, pitch-shifted version of `self.music_mode_sample` will be generated in memory. The pitch shift algorithm should be fast enough for real-time performance.
        *   The resulting audio will be played immediately. This will likely involve exporting the shifted sample to a temporary `BytesIO` object and playing it with a new `just_playback` instance to allow for polyphony.

4.  **Mode Deactivation:**
    *   When the spacebar is pressed again, `self.music_mode` is set to `False`, and `self.music_mode_sample` is cleared. The keyboard event logic in `OS.kick` will revert to its normal behavior.
