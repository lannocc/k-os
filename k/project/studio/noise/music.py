from wavefile import WaveReader, WaveWriter
#import pyaudio

def musify(trk):
    #p = pyaudio.PyAudio()

    with WaveReader(trk.res.afn) as r:
        print(f'OPENED channels:{r.channels} rate:{r.samplerate}')

        #out = p.open(
        #    format = pyaudio.paFloat32,
        #    channels = r.channels,
        #    rate = r.samplerate,
        #    frames_per_buffer = 512,
        #    output = True)

        skip = (trk.begin / trk.res.fps) * r.samplerate
        count = (trk.frames / trk.res.fps) * -1 * r.samplerate
        alt = None
        buf = 16

        with WaveWriter('out.wav',
                        channels=r.channels,
                        samplerate=int(r.samplerate/1)) as w:
            try:
                for frame in r.read_iter(size=int(skip)):
                    skip = 0
                    break

                for frame in r.read_iter(size=buf):
                    if skip > 0:
                        skip -= buf
                    elif skip <= count:
                        break
                    else:
                        skip -= buf
                        #out.write(frame.flatten(), frame.shape[1])

                        if alt:
                            alt = False
                        else:
                            w.write(frame)
                            if alt is not None:
                                alt = True

            except StopIteration:
                print('EXIT')
                return

    print('done')

