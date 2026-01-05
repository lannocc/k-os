@%@~LICENSE:OK~@%@

K-OS
====

ORDER IN CHAOS

This is the "K" Operating System. K in this context stands in for many things such as keyframe or knife, or ken, but also generically.

Purpose:

* make art
* play video
* hack python
* perform musically
* train logic (AI)
* grow fun community

From a complete and fully-formed object / idea to noise, randomness, or the absence of anything... there are those points where change occurs and entropy is added; that is K.

---

Developed using Python 3.9.6 on Gentoo (pygame 2.1.0 / pytube / ffmpeg 4.4).

Run the file named: start.py
 in this directory

Examples:: ./start.py
           python3 start.py


  (Optional) DIP-switches
[ specify on command-line ]

    0: No Meta
    1: Single-Threaded (No ImageEngine)
    2: No Online
    3: No Governor
    4: No Shadow
    6: No Replay
    9: Full-Screen

Examples:: ./start.py 206
           python3 start.py 91


Folders
-------

Folders in this project directory are used as follows:

    + a - ack/art/annotated (blackboard saves)
    + d - downloaded media (YouTube)
    + g - graphics
    + k - killer source code (python!)
    + p - project stuff (thumbnails)
    + r - replay capture (screenshots)
    + w - web ui (svelte)


== WEB UI ==

=== Backend ===

Activate virtual environment...
```
python -m venv venv
source venv/bin/activate
```

...then install the dependencies...
```
pip install -r requirements.txt
```

...and launch:
```
./svelte.py
```

=== Frontend ===

Install the dependencies...

```
npm install
```

...and launch ([Rollup](https://rollupjs.org)):

```
npm run dev
```

Navigate to [localhost:8080](http://localhost:8989).


== Author ==

by LANNOCC

