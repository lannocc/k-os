import k.db as kdb

from os import mkdir, listdir
from os.path import join, exists
from urllib.request import urlretrieve
import xml.etree.ElementTree as ET
from subprocess import run, Popen
import shutil
from datetime import datetime
from io import BytesIO
import tempfile


ACKS = 'a'
#BLEEDS = 'b'
#CAMS = 'c'
GFX = 'g'
DOWNLOADS = 'd'
PROJECTS = 'p'
#FOCUS = 'f'
REPLAYS = 'r'
TEMP = tempfile.gettempdir()


def get_gfx(filename):
    import pygame.image
    return pygame.image.load(join(GFX, filename))

def get_video_filename(yt_channel_id, yt_video_id, yt_itag, extension):
    return join(DOWNLOADS, yt_channel_id,
        f'{yt_video_id}.{yt_itag}.{extension}')

def get_video_thumbnail(yt_channel_id, yt_video_id):
    return join(DOWNLOADS, yt_channel_id, f'{yt_video_id}.jpg')

def get_audio_filename(yt_channel_id, yt_video_id):
    return join(DOWNLOADS, yt_channel_id, f'{yt_video_id}.wav')

def get_frag_thumbnail(project_id, frag_id):
    return join(PROJECTS, str(project_id), f'{frag_id}.jpg')

def start_project(project_id):
    folder = join(PROJECTS, str(project_id))
    print(f'creating project folder: {folder}')
    mkdir(folder)

def copy_thumbnail(video_id, project_id, frag_id):
    video = kdb.get_video(video_id)
    channel = kdb.get_channel(video['channel'])
    src = get_video_thumbnail(channel['ytid'], video['ytid'])
    dst = get_frag_thumbnail(project_id, frag_id)
    shutil.copyfile(src, dst)

def finish_adding_video(video_id):
    #from pytube import YouTube
    from pytubefix import YouTube
    video = kdb.get_video(video_id)
    url = 'https://youtu.be/' + video['ytid']
    add_video_to_library(YouTube(url), video_id)

def add_video_to_library(video, video_id=None):
    #from pytube import Channel
    from pytubefix import Channel
    print(f'add to: {DOWNLOADS}/')

    channel_id = kdb.id_channel(video.channel_id)
    print(f'channel: {channel_id}')
    channel = Channel(video.channel_url)

    if channel_id:
        kdb.update_channel(channel_id, channel)
    else:
        channel_id = kdb.insert_channel(channel)
        try:
            mkdir(join(DOWNLOADS, video.channel_id))
        except FileExistsError:
            pass

    if video_id:
        kdb.update_video(video_id, video)
    else:
        video_id = kdb.insert_video(channel_id, video)
    folder = join(DOWNLOADS, video.channel_id)

    thumbnail = join(folder, f'{video.video_id}.jpg')
    urlretrieve(video.thumbnail_url, thumbnail)

    for keyword in video.keywords:
        kdb.insert_keyword(video_id, keyword)

    print('video streams available:')
    print(video.streams)

    stream = video.streams.get_lowest_resolution()
    if not stream:
        stream = video.streams.order_by('resolution').first()
    stream_id = kdb.insert_stream(video_id, stream)

    print(f'downloading {stream}...')
    stream.download(folder, f'{video.video_id}.{stream.itag}.{stream.subtype}')
    print('   download complete')

    captions = None
    try:
        captions = video.captions['en']
    except KeyError:
        try:
            captions = video.captions['a.en']
        except KeyError:
            pass

    if captions:
        print(f'   captions lang: {captions.code}')
        filename = f'{video.video_id}.{captions.code}.xml'
        xml = join(folder, filename)

        #FIXME  pytube caption converter is broken right now?
        #captions.download(folder, filename)

        with open(xml, 'w') as outfile:
            outfile.write(captions.xml_captions)

        # Replaced system call to xsltproc with Python's built-in XML parser
        # for cross-platform compatibility. This removes the dependency on xsltproc.
        root = ET.fromstring(captions.xml_captions)
        all_text = " ".join(root.itertext())
        text = " ".join(all_text.split())

        captions_id = kdb.insert_captions(video_id, captions, text)

        if root.tag == 'timedtext':
            caps = [ ]
            _recurse_captions_(caps, captions_id, 0, root)
            print(f'   inserting {len(caps)} rows...')
            count = kdb.insert_caption_list(caps)
            print(f'      {count} rows inserted')

        else:
            print(f'   UNSUPPORTED captions type: {root.tag}')

    else:
        print('   no captions')

    return video_id

def _recurse_captions_(caps, captions_id, start, elem):
    if 't' in elem.attrib:
        start += int(elem.attrib['t'])

    text = elem.text
    if text:
        text = text.strip().replace('\n', ' ')
    if text:
        #print(f'{start}: {text}')
        #kdb.insert_caption(captions_id, start, text)
        caps.append((captions_id, start, text))

    for child in elem:
        _recurse_captions_(caps, captions_id, start, child)

def extract_audio_from_video(video_id):
    video = kdb.list_video(video_id)
    stream = kdb.list_video_streams(video_id)[0] #FIXME
    vfn = get_video_filename(video['cytid'], video['ytid'],
        stream['itag'], stream['subtype'])
    afn = get_audio_filename(video['cytid'], video['ytid'])
    extract_audio(vfn, afn)

def extract_audio(vfn, afn):
    from moviepy.editor import VideoFileClip

    print(f'extracting audio: {afn}')

    if exists(afn):
        print(f'   audio file already exists, skipping: {afn}')
        return

    # Replaced system call to ffmpeg with moviepy for cross-platform
    # compatibility. This removes the dependency on a system-installed ffmpeg.
    try:
        with VideoFileClip(vfn) as video_clip:
            if video_clip.audio:
                # logger=None silences the output from write_audiofile
                video_clip.audio.write_audiofile(afn, logger=None)
                print('   extraction complete')
            else:
                print(f"   Warning: No audio track found in {vfn}")
    except Exception as e:
        print(f"   An error occurred during audio extraction from {vfn}: {e}")

'''
def focus_peek(me=True, delay=None):
    #print('peekaboo! :-P')
    dt = datetime.now().strftime('%Y-%m-%d_%H-%M-%S_%f')

    cmd = [
        'spectacle',
        '--background', '--nonotify',
    ]

    if me:
        cmd.extend([
            '--output', join(FOCUS, f'{dt}.k.png'),
            '--activewindow', '--no-decoration',
        ])

    else:
        cmd.extend([
            '--output', join(FOCUS, f'{dt}.desk.png'),
            '--fullscreen',
        ])

    if delay:
        cmd.extend(['--delay', str(delay)])

    # FIXME - system call to spectacle
    #run(cmd)
    return Popen(cmd, shell=False, stdin=None, stdout=None, stderr=None,
        close_fds=True)
'''

def start_replay(replay_id):
    folder = join(REPLAYS, str(replay_id))
    print(f'creating replay folder: {folder}')
    mkdir(folder)

def save_replay_image(replay_id, surface, name):
    import pygame.image
    fn = join(REPLAYS, str(replay_id), f'{name}.png')
    pygame.image.save(surface, fn)

def list_replay_images(replay_id=None):
    names = [ ]

    if replay_id is not None:
        for fn in listdir(join(REPLAYS, str(replay_id))):
            if not fn.endswith('.png'):
                continue

            names.append(fn[:-4])

    else:
        for rid in listdir(REPLAYS):
            if not rid.startswith('.'):
                names.append(int(rid))

    return names

def get_replay_image(replay_id, name):
    import pygame.image
    return pygame.image.load(join(REPLAYS, str(replay_id), f'{name}.png'))

def save_ack_image(surface, name):
    import pygame.image
    fn = join(ACKS, f'{name}.png')
    pygame.image.save(surface, fn)

def list_ack_images():
    names = [ ]

    for fn in listdir(ACKS):
        if not fn.endswith('.png'):
            continue

        names.append(fn[:-4])

    return names

def get_ack_image(name):
    import pygame.image
    return pygame.image.load(join(ACKS, f'{name}.png'))

'''
    The pygame scrap system (clipboard) is only giving me text/plain entries.
    Any binary data (e.g. image/png) isn't working on my system.
    So we implement it ourselves here using the xclip system command.
        -lannocc
'''
def put_clipboard_image(surface):
    import pygame.image
    #fn = join(TEMP, 'k-os_clipboard')
    #with open(fn, 'wb') as out:
    #    out.write(data)
    #return fn

    with BytesIO() as io:
        pygame.image.save(surface, io, 'clipboard.png')
        # FIXME: system call to xclip
        run(['xclip', '-selection', 'clipboard', '-i', '-t', 'image/png'],
            input=io.getvalue(), check=True)

def get_clipboard_image():
    # FIXME: system call to xclip
    xclip = run(['xclip', '-selection', 'clipboard', '-o', '-t', 'TARGETS'],
        capture_output=True, text=True, check=True)

    targets = xclip.stdout.split('\n')

    if 'image/png' in targets:
        return _get_clipboard_image_('image/png')

    else:
        for target in targets:
            if target.startswith('image/'):
                try:
                    return _get_clipboard_image_(target)

                except pygame.error:
                    pass

    return None

def _get_clipboard_image_(target):
    import pygame.image
    assert target.startswith('image/')

    # FIXME: system call to xclip
    xclip = run(['xclip', '-selection', 'clipboard', '-o', '-t', target],
        capture_output=True, check=True)

    with BytesIO(xclip.stdout) as io:
        return pygame.image.load(io, f'clipboard.{target[6:]}')

def save_palette(surf):
    import pygame.image
    fn = join(GFX, 'palette.png')
    pygame.image.save(surf, fn)

def load_palette():
    import pygame.image
    fn = join(GFX, 'palette.png')
    if not exists(fn):
        return None

    return pygame.image.load(fn)
