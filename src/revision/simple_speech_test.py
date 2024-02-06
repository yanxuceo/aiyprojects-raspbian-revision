import io
from google.oauth2 import service_account
from google.cloud import speech

from google.cloud.speech import StreamingRecognitionConfig, RecognitionConfig, RecognitionAudio


client_file = '/home/pi/cloud_speech.json'
credentials = service_account.Credentials.from_service_account_file(client_file)
client = speech.SpeechClient(credentials=credentials)

audio_file = '/home/pi/aiyprojects-raspbian-revision/src/revision/test3.wav'
with io.open(audio_file, 'rb') as f:
    content = f.read()
    audio = speech.RecognitionAudio(content=content)


config = speech.RecognitionConfig(
    encoding = speech.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=48000,
    audio_channel_count = 2,
    language_code='en-US'
)

#response = client.recognize(config=config, audio=audio)
#print(response)
#print(response.results[0].alternatives)


streaming_config = StreamingRecognitionConfig(
    config=RecognitionConfig(
        encoding=RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=48000,
        language_code='en-US',
        audio_channel_count=2,
        # Enable automatic punctuation
        enable_automatic_punctuation=True
    ),
    # Set to `True` to return interim results (useful for real-time feedback)
    interim_results=True,
    single_utterance=True
)

def generate_streaming_requests(audio_file):
    """Generator function that yields StreamingRecognizeRequest messages."""
    with io.open(audio_file, 'rb') as audio_stream:
        while True:
            data = audio_stream.read(4096)  # Or another chunk size
            if not data:
                break
            yield speech.StreamingRecognizeRequest(audio_content=data)


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
    #play_wav(args.filename)



    responses = client.streaming_recognize(config=streaming_config, requests=generate_streaming_requests(args.filename))

    for response in responses:
        # Check each result in the response
        for result in response.results:
            # When is_final is True, the API has determined the end of an utterance
            if result.is_final:
                print(f"Final transcript: {result.alternatives[0].transcript}")
                # Here, you might choose to break out of the loop if you are only interested in the first utterance
                # Or you can continue processing further results as needed

                # If you set single_utterance to True in your StreamingRecognitionConfig,
                # the server will typically close the stream after returning the first is_final result,
                # so you may not need to explicitly break here





    print('Done.')

    # Don't forget to close the button when done
    button.close()

if __name__ == '__main__':
    main()
