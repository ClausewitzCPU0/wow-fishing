import audioop
import pyaudio
import time


rms = 0
n = 0
chunk = 1024
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,
                channels=2,  # need this to work (like other record script)
                rate=44100,
                input=True,
                frames_per_buffer=chunk)

while True:
    data = stream.read(chunk)
    rms = audioop.rms(data, 2)  # width=2 for format=paInt16
    if n == 5:  # only print out every 10th one
        print('rms value = %d' % rms)
        n = 0
    else:
        n = n + 1

    time.sleep(.1)
