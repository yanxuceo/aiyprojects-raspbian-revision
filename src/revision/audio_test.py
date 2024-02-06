import argparse
import time
import threading

from button_class import Button 
from audio_class import AudioFormat, play_wav, record_file, Recorder


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', '-f', default='recording.wav')
    args = parser.parse_args()

    # Initialize your custom Button instance (replace 'D17' with the actual GPIO pin you're using)
    button = Button('D17')

    print('Press button to start recording.')
    button.wait_for_press()

    done = threading.Event()
    button.when_pressed = done.set  # Assuming your Button class has a when_pressed property

    def wait():
        start = time.monotonic()
        while not done.is_set():
            duration = time.monotonic() - start
            print('Recording: %.02f seconds [Press button to stop]' % duration)
            time.sleep(0.5)

    record_file(AudioFormat.CD, filename=args.filename, wait=wait, filetype='wav')
    print('Press button to play recorded sound.')
    button.wait_for_press()

    print('Playing...')
    play_wav(args.filename)
    print('Done.')

    # Don't forget to close the button when done
    button.close()

if __name__ == '__main__':
    main()
