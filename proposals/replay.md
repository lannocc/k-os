# Replay System Overhaul and Project Portability

**Status:** Implemented

This document outlines a proposal to complete the vision for the k-os replay system. The goal is to move from low-level input recording to high-level semantic action recording, unify the action systems, improve performance through proactive caching, and introduce a comprehensive project import/export feature.

## 1. Semantic Player Action Recording

### A. Summary

The current replay system primarily records low-level UI events like `KeyDown` and `MouseMove`. This is insufficient for robustly replaying complex player interactions. For example, holding the "hold" key (`Numpad .`) results in a stream of repeated seek actions being recorded, rather than the user's intent to "hold".

This proposal introduces the concept of recording high-level, semantic **Player Actions**. This will make replays more accurate, more robust against future keybinding changes, and will unify the action recording logic used by both the main replay system and the F-key loop track recorder.

### B. Implementation Plan

1.  **Define New Semantic Actions (`k/player/actions.py`)**
    *   The existing `PlayerAction` system will be expanded to include actions that represent user intent rather than raw input. New classes will be added:
        *   `PlayerHoldStart()`: Recorded when the hold key is first pressed.
        *   `PlayerHoldEnd()`: Recorded when the hold key is released.
        *   `PlayerJump(index)`: Recorded when a numpad jump key (1-9) is pressed.
        *   `PlayerSetLoopStart()`: Records that the current frame is the new loop start point.
        *   `PlayerSetLoopEnd()`: Records that the current frame is the new loop end point.
        *   `PlayerLoopToggle(state)`: Records the loop mode being turned on or off.
        *   `PlayerPlaybackSpeed(speed, direction)`: A new action to replace `PlayerSetSpeed`, explicitly capturing changes to speed and direction.

2.  **Generate Actions in Player UI (`k/player/ui.py`)**
    *   The `Player.keydown` method will be refactored. Instead of just executing logic, it will now instantiate the appropriate semantic `PlayerAction` objects.
    *   For example, when `pygame.K_KP_PERIOD` is pressed, instead of just setting a hold flag, the code will now create a `PlayerHoldStart()` action.

3.  **Unify Action Recording**
    *   Both the main replay system and the F-key loop recorder will consume these new semantic actions.
    *   **In `k/player/ui.py`:** When a semantic action is generated, the code will check the global state and pass the action to the appropriate recorder(s):
        *   If `self.k.f_key_capturing` is true, the action will be appended to `self.k.f_key_current_actions`.
        *   If `self.k.replays` is true, the action will be passed to the main replay system via `self.k.replay_op(action)`.
    *   **In `k/replay/__init__.py`:** The `Panel.op()` method will be updated to accept and serialize these new `PlayerAction` types, saving them alongside the low-level UI events. This creates a complete record of the user's session.
    *   The `PlayerPlay`, `PlayerPause`, etc. actions already defined in `k/player/actions.py` will also be integrated into the main replay system in the same way.

## 2. Proactive Audio Caching

### A. Summary

Currently, audio for F-key loops and number-key samples is loaded from the source video and sliced on-demand. This can introduce a slight delay the first time a loop or sample is played. To improve performance and responsiveness, this proposal introduces a proactive caching system that processes and saves these audio snippets to disk.

### B. Implementation Plan

1.  **New Cache Directory Structure**
    *   A new directory will be created within each project's folder to store cached audio: `p/<project_id>/cache/`.

2.  **F-Key Loop Caching**
    *   **On Project Load (`k/project/studio/__init__.py`):** The `Panel.open_project` method will be modified. After loading the `f_key_loops` from the database, it will iterate through them.
    *   For any loop that contains `music_context_json`, a background job will be triggered to:
        1.  Load the source audio file using `k.storage.get_audio()`.
        2.  Slice the audio segment using `pydub`.
        3.  Save the resulting `AudioSegment` as a `.wav` file to `p/<project_id>/cache/fkey_<fkey_code>.wav`.
        4.  Update the in-memory `self.k.f_key_loops` dictionary entry to replace `music_context_json` with a direct path to this cached file.
    *   **In `k/player/loop.py`:** The `LoopPlayer` and `MicroMusicPlayer` will be updated to first check for a cached file path. If it exists, they will load the pre-sliced `.wav` directly, bypassing the need to load and slice the original large audio file.

3.  **Clip Sample Caching**
    *   **On Clip Play (`k/project/studio/clip.py`):** The `Entry.play` method, which is called whenever a clip is played (either from the UI or a hotkey), will be updated. If the player starts in music mode, it will immediately call a new method, e.g., `self.k.music.cache_all_slots_for_player(player)`.
    *   **On Music Mode Toggle (`k/player/ui.py`):** The `Player.keydown` logic that handles toggling music mode will also be updated. When music mode is turned *on*, it will call `self.k.music.cache_all_slots_for_player(self)` to ensure samples are cached.
    *   **In `k/player/music.py`:**
        *   A new method `cache_all_slots_for_player` will iterate through the `player.selection_regions`.
        *   The existing `cache_sample_for_slot` logic will be modified to save the sliced `AudioSegment` to `p/<project_id>/cache/clip_<frag_id>_slot_<key_code>.wav`.
        *   The `self.slotted_samples` dictionary will be updated to store paths to these cached files instead of large in-memory `AudioSegment` objects.

## 3. Persistent Volume Levels

### A. Summary

The application allows adjusting the volume of individual F-key loop tracks and number-key samples. While sample volume is persisted, F-key loop volume is not, resetting when the application restarts. This proposal ensures all volume changes are saved automatically.

### B. Implementation Plan

In the `Player.keydown` method in `k/player/ui.py`, the logic that handles volume changes via `PageUp`/`PageDown` when an F-key is held will be updated. Currently, this code updates the volume in the in-memory dictionary: `self.k.f_key_loops[held_f_key]['volume'] = new_volume`. Immediately after this line, a call will be added to persist this change to the database. This will require gathering all necessary data from the `loop_data` object and the project context to call `kdb.upsert_f_track`.

**F-Key Loop Volume (`k/player/ui.py`)**
*   In the `Player.keydown` method, locate the logic that handles volume changes via `PageUp`/`PageDown` when an F-key is held.
*   Currently, this code updates the volume in the in-memory dictionary: `self.k.f_key_loops[held_f_key]['volume'] = new_volume`.
*   Immediately after this line, a call will be added to persist this change to the database. This will require gathering all necessary data from the `loop_data` object and the project context to call `kdb.upsert_f_track`.

## 4. Project Import/Export

### A. Summary

To allow for collaboration and project backup, a feature to export a project into a single, portable ASCII file (`.k`) and import it on another system will be implemented. The export will contain only the necessary database information, not binary assets. Since all media is sourced from YouTube, the target system will re-download or re-generate any required assets (like video files, audio, and thumbnails) on demand, ensuring the project file remains small and easily shareable.

### B. Implementation Plan

1.  **Export Format (`.k` file)**
    *   A project will be exported as a single, human-readable JSON file with a `.k` extension.
    *   The root JSON object will act as a container, allowing future expansion for different data types. For this feature, it will be structured as follows:
        ```json
        {
          "type": "k-os project export",
          "version": "1.14 adamcarolla 19+31 /6",
          "data": {
            "project": { ... },
            "channels": [ { ... } ],
            "videos": [ { ... } ],
            "fragments": [ { ... } ],
            "clips": [ { ... } ],
            "sequences": [ { ... } ],
            "segments": [ { ... } ],
            "f_tracks": [ { ... } ]
          }
        }
        ```
    *   The `data` object will contain all database rows related to the project. Original database IDs will be included to preserve relationships within the exported data, which will be remapped during import.

2.  **Export UI and Logic (`k/project/library.py`)**
    *   An "Export" button will be added to each project `Entry` in the project library.
    *   The click handler will:
        1.  Prompt the user for a save location for the `.k` file.
        2.  **Gather Project Data:**
            a. Query the database for the project's details and all its associated `f_tracks`, `fragments`, `clips`, `sequences`, and `segments`.
            b. From the collected fragments, compile a unique set of `video_id`s used in the project.
            c. Query the `video` table for all details of these videos, including their `ytid` and `channel` ID.
            d. From the collected videos, compile a unique set of `channel_id`s.
            e. Query the `channel` table for all details of these channels, including their `ytid`.
        3.  **Construct the Manifest:**
            a. Create the root JSON object, setting the `type` to `"k-os project export"`.
            b. Read the `VVHEN` version string from `version.py` and assign it to the `version` key.
            c. Populate the `data` key with the lists of database objects (project, channels, videos, etc.).
        4.  **Write to File:**
            a. Serialize the complete JSON object into a formatted string.
            b. Write the string to the selected file path. No binary data or zip archives will be created.

3.  **Import UI and Logic (`k/project/library.py`)**
    *   A global "Import Project..." button will be added to the project library panel.
    *   The click handler will:
        1.  Prompt the user to select a `.k` file.
        2.  Read and parse the JSON file. Verify the `type` is correct and note the `version`.
        3.  **Perform ID Remapping and Insertion within a database transaction:**
            a. **Channels & Videos:** For each channel and video in the manifest, check the local database for an existing entry via its `ytid`.
                *   If it doesn't exist, insert a new record using the data from the manifest. The video will be added without its binary file, which can be downloaded by the user later.
                *   Build maps to translate from `manifest_channel_id -> local_channel_id` and `manifest_video_id -> local_video_id`.
            b. **Project:** Insert the project data to create a new project, yielding a `new_project_id`.
            c. **Dependent Data:** Insert the `fragments`, `clips`, `sequences`, `segments`, and `f_tracks` from the manifest. As each row is inserted, use the ID maps created in the previous steps to resolve all foreign key relationships (e.g., `project_id`, `source` video, `fragment_id`) to their new, local values.
            d. Commit the transaction.
        4.  **Post-Import Handling:**
            a. The imported project will now appear in the library.
            b. Assets are not included in the import. When the user interacts with the project (e.g., opens a clip), the application will detect that the underlying video/audio assets are missing and will trigger the standard download and processing workflow. Thumbnails for fragments will be generated on-demand.
            c. Refresh the project library view to show the newly imported project.
