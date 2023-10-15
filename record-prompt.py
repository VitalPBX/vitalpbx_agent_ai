#!/usr/bin/env python3
import sys
import os
import time
from dotenv import load_dotenv 
from pydub import AudioSegment
import azure.cognitiveservices.speech as speechsdk

load_dotenv("/var/lib/asterisk/agi-bin/.env")
AZURE_SPEECH_KEY = os.environ.get('AZURE_SPEECH_KEY')
AZURE_SERVICE_REGION = os.environ.get('AZURE_SERVICE_REGION')

# The format to record a prompt is as follows:
# ./record-prompt.py file-name "Text to record" language
# file-name --> file name if extension mp3, remember that in the Agent AI script, the welcome audio is: welcome-en (English), welcome-es (Spanish), and the wait audio is: wait-en (English), and wait-es (Spanish).
# languaje --> could be "en-US" or "es-ES"
# If you want to add more languages you must modify the scripts

# Check if a file name was provided
audio_name = sys.argv[1] if len(sys.argv) > 1 else None
audio_text = sys.argv[2] if len(sys.argv) > 1 else None
language = sys.argv[3] if len(sys.argv) > 1 else None

if audio_name is None:
    print("No filename provided for the recording.")
    sys.exit(1)

if audio_text is None:
    print("No text to record audio.")
    sys.exit(1)

if language == "es-ES":
    azure_language = "es-ES" 
    azure_voice_name = "es-ES-ElviraNeural"
else:
    azure_language = "en-US" 
    azure_voice_name = "en-US-JennyNeural"

audio_path = f"/var/lib/asterisk/sounds/{audio_name}.mp3"
print(audio_path)

def main():

    # Sets API Key and Region
    speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_SERVICE_REGION)

    # Sets the synthesis output format.
    # The full list of supported format can be found here:
    # https://docs.microsoft.com/azure/cognitive-services/speech-service/rest-text-to-speech#audio-outputs
    speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3)

    # Select synthesis language and voice
    # Set either the `SpeechSynthesisVoiceName` or `SpeechSynthesisLanguage`.
    speech_config.speech_synthesis_language = azure_language 
    speech_config.speech_synthesis_voice_name = azure_voice_name

    # Creates a speech synthesizer using file as audio output.
    # Replace with your own audio file name.
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
    result = speech_synthesizer.speak_text_async(audio_text).get()
 
    stream = speechsdk.AudioDataStream(result)
    stream.save_to_wav_file(audio_path)

    # Path to the original MP3 file and path for the trimmed file
    original_file = audio_path
    trimmed_file = "/tmp/tmp.mp3"

    # Load the original audio file in MP3 format
    audio = AudioSegment.from_mp3(original_file)

    # Get the total duration of the file in milliseconds
    total_duration = len(audio)

    # Calculate the new duration without the last second
    new_duration = total_duration - 750  # Subtract 1000 milliseconds (1 second)

    # Trim the audio file
    trimmed_audio = audio[:new_duration]

    # Save the trimmed file as MP3
    trimmed_audio.export(trimmed_file, format="mp3")

    # Remove the original file
    os.remove(original_file)

    # Rename the trimmed file to the original file name
    os.rename(trimmed_file, original_file)

if __name__ == "__main__":
    main()
