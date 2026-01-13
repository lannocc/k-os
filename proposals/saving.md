# Project Saving Expansion: Loops and Samples

**Status:** Proposed

This document outlines a proposal to expand the project saving functionality to include the persistence of music performance data. Specifically, this covers the F-key audio loop tracks and the number-key saved samples, making them integral parts of a project that can be saved and restored across sessions.

## 1. High-Level Summary

The goal is to make the powerful live performance features introduced in the Music Mode proposal a persistent part of the creative process. This will be achieved by saving their state into the project database.

-   **F-Key Loop Tracks:** These are global performance elements. As such, they will be scoped to the **project**. Opening a project will restore all its associated F-key loops.
-   **Number-Key Saved Samples:** These are selections from specific clips. They will be scoped to the **clip** from which they were created. Playing a clip will make its saved samples available.

All saving and loading will happen automatically in the background. There will be no new "Save" buttons in the UI for this functionality. The changes will involve modifications to the database schema and updates to the project and player loading/saving logic.

## 2. Saving Project-Scoped Loop Tracks

The state of all 12 F-key loops, currently stored in-memory in `OS.f_key_loops`, will be saved to the database and associated with the currently open project.

### Database Schema Changes

A new table, `f_track`, will be created to store the loop data.

```sql
CREATE TABLE IF NOT EXISTS f_track (
    project             INTEGER NOT NULL,
    fkey                INTEGER NOT NULL, -- The pygame keycode (e.g., K_F1)
    actions             TEXT NOT NULL,
    duration            REAL NOT NULL,
    volume              REAL NOT NULL DEFAULT 0.5,
    locked              BOOLEAN NOT NULL DEFAULT 0,
    music_context_json  TEXT, -- JSON storing sample source info

    PRIMARY KEY (project, fkey),
    FOREIGN KEY (project) REFERENCES project (id)
);
```

-   **`actions`**: Will store the list of `PlayerAction` objects, serialized into a single string (e.g., newline-separated).
-   **`music_context_json`**: The in-memory `music_context` contains a `pydub` `AudioSegment` object which cannot be directly saved. Instead, we will store a JSON object with the information needed to recreate it: the source video ID and the start/end frames of the audio sample. Example: `"{'source_video_id': 101, 'start_frame': 1500, 'end_frame': 2500}"`.

### Implementation Plan

1.  **Database Layer (`k/db.py`)**
    *   Add the `CREATE TABLE` statement for `f_track`.
    *   Create new data access functions:
        *   `upsert_f_track(project_id, fkey, data)`: Inserts or updates a loop's data.
        *   `delete_f_track(project_id, fkey)`: Removes a loop from the database.
        *   `list_f_tracks(project_id)`: Retrieves all loops for a given project.

2.  **Saving Logic (`k/K.py`)**
    *   The `OS` class methods that modify `self.f_key_loops` will be updated to call the new database functions, but only if a project is active (`self.panel_project.panel_studio.project_id` is not `None`).
    *   **`save_captured_loop_to_slot`**: After successfully creating a loop dictionary, it will call `kdb.upsert_f_track`.
        *   The `actions` list will be serialized by calling `action.format()` on each `PlayerAction` and joining them with newlines.
        *   The `music_context` will be converted for storage. Instead of storing the `pydub` object, we will find the source `video_id` from the active player's resource and create the JSON string.
    *   **`kick` (Key Event Handler)**:
        *   When a loop is deleted with `Backspace + F-key`, it will call `kdb.delete_f_track`.
        *   When a loop's locked state is toggled with `Ctrl + F-key`, it will call `kdb.upsert_f_track` to update the `locked` flag.

3.  **Loading Logic**
    *   **`k/project/studio/__init__.py`**: The `Panel.open_project` method will be modified.
        *   After loading the project details, it will call `kdb.list_f_tracks(project_id)`.
        *   It will then clear `self.k.f_key_loops` and repopulate it by parsing the data returned from the database.
        *   Action strings will be deserialized back into `PlayerAction` objects using a parser that complements the `format()` method.
    *   **`k/player/loop.py`**: The `LoopPlayer` class will be updated.
        *   Its `__init__` method will be changed to accept the `music_context_json` data instead of a pre-loaded `pydub` sample.
        *   Upon initialization, if context is present, the `LoopPlayer` (or its `MicroMusicPlayer`) will be responsible for loading the audio file and slicing the sample itself, making it self-contained.

## 3. Saving Clip-Scoped Samples

The state of the 10 number-key sample slots, currently stored in-memory in `Player.selection_regions`, will be saved to the database and associated with their parent clip.

### Database Schema Changes

The existing `clip` table will be modified to store the sample data.

-   In `k/db.py`, a new column will be added to the `clip` table:
    *   `selection_regions TEXT`
-   This column will store a JSON-serialized representation of the `selection_regions` dictionary. Example: `"{'1073741913': [100, 200, 1.0, false], '1073741914': [350, 500, 0.8, true]}"` (where the keys are pygame keycodes).

### Implementation Plan

1.  **Database Layer (`k/db.py`)**
    *   Add the `selection_regions` column to the `clip` table definition.
    *   Create a new function `set_clip_selection_regions(frag_id, regions_dict_json)`.
    *   Update `get_clip_listing` and `list_clips` to also retrieve the `selection_regions` column.

2.  **Saving Logic (`k/player/ui.py`)**
    *   In the `Player.keydown` method, the logic that handles saving and locking samples will be updated.
    *   When `pygame.K_SPACE` is pressed to save a new sample region, or when `Ctrl + Number-key` is used to toggle a lock:
        *   After the in-memory `self.selection_regions` dictionary is modified, a new call will be made: `kdb.set_clip_selection_regions(self.clip_id, json.dumps(self.selection_regions))`.
        *   The `Player` class already has access to its `clip_id` (via the `frag_id` on the `Chaos` wrapper).

3.  **Loading Logic**
    *   **`k/project/studio/clip.py`**:
        *   The `Entry.play` method, which instantiates a player for a clip, will be updated.
        *   When it fetches clip data from the database, it will now also receive the `selection_regions` JSON string.
        *   This string will be passed as a new argument to the `Player` constructor.
    *   **`k/player/ui.py`**:
        *   The `Player.__init__` method will be updated to accept the `selection_regions` JSON string.
        *   If the string is not null, it will be deserialized using `json.loads`.
        *   Because JSON object keys must be strings, the string keycodes will be converted back to integers before populating `self.selection_regions`.

## 4. Database Migration

To apply these changes to existing user databases, a new patch file, `k/patch/v8.py`, will be required. This patch will execute two main SQL commands:

1.  **Create `f_track` table:**
    ```sql
    CREATE TABLE f_track (
        project INTEGER NOT NULL,
        fkey INTEGER NOT NULL,
        actions TEXT NOT NULL,
        duration REAL NOT NULL,
        volume REAL NOT NULL DEFAULT 0.5,
        locked BOOLEAN NOT NULL DEFAULT 0,
        music_context_json TEXT,
        PRIMARY KEY (project, fkey),
        FOREIGN KEY (project) REFERENCES project (id)
    );
    ```

2.  **Alter `clip` table:**
    ```sql
    ALTER TABLE clip ADD COLUMN selection_regions TEXT;
    ```

