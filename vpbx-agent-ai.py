#!/usr/bin/env python3
import sys
import os
import openai
import time
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk

# For Asterisk AGI
from asterisk.agi import *

load_dotenv("/var/lib/asterisk/agi-bin/.env")
AZURE_SPEECH_KEY = os.environ.get('AZURE_SPEECH_KEY')
AZURE_SERVICE_REGION = os.environ.get('AZURE_SERVICE_REGION')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

agi = AGI()

# Check if a file name was provided
uniquedid = sys.argv[1] if len(sys.argv) > 1 else None
language = sys.argv[2] if len(sys.argv) > 1 else None

if uniquedid is None:
    print("No filename provided for the recording.")
    sys.exit(1)

# Check if a file name was provided
recording_path = f"/tmp/rec{uniquedid}"
answer_path = f"/tmp/ans{uniquedid}.mp3"
pa_file = f"/tmp/pa{uniquedid}.txt"

if language == "es-ES":
    azure_language = "es-ES" 
    azure_voice_name = "es-ES-ElviraNeural"
    wait_message = "/var/lib/asterisk/sounds/wait-es.mp3"
    short_message = "/var/lib/asterisk/sounds/short-message-es.mp3"
else:
    azure_language = "en-US" 
    azure_voice_name = "en-US-JennyNeural"
    wait_message = "/var/lib/asterisk/sounds/wait-en.mp3"
    short_message = "/var/lib/asterisk/sounds/short-message-en.mp3"

def main():

    try:

        # We send the 'raw' command to record the audio, q--> no beep, 3 second of silences
        sys.stdout.write('EXEC Record ' + recording_path + '.wav,3,30,y\n')
        sys.stdout.flush()
        # We await Asterisk's response
        result = sys.stdin.readline().strip()

        if result.startswith("200 result="):

            # Play wait message.
            agi.appexec('MP3Player', wait_message)
           
            #DEBUG
            agi.verbose("Successful Recording",2)

            # Once everything is fine, we send the audio to OpenAI Whisper to convert it to Text
            openai.api_key = OPENAI_API_KEY
            audio_file = open(recording_path + ".wav", "rb")
            transcript = openai.Audio.transcribe("whisper-1", audio_file)

	    # If nothing is recorded, Whisper returns "you", so you have to ask again.
            if transcript.text == "you":
                agi.appexec('MP3Player', short_message)
                agi.verbose("Message too short",2)
                sys.exit(1)

            #DEBUG
            agi.verbose(transcript.text,2)

	    # Find the previous question, with the idea of keeping the conversation
            if os.path.exists(pa_file):
                with open(pa_file, 'r') as previous_file:
                    previous_question = previous_file.readline().strip()
            else:
                previous_question = ""

            messages = []
            messages.append({"role": "user", "content": transcript.text})
            messages.append({"role": "assistant", "content": previous_question})
            response = openai.ChatCompletion.create(
                       model="gpt-3.5-turbo",
                       messages=messages
                       )
            chatgpt_answer = response['choices'][0]['message']['content']

            # save current answer
            with open(pa_file, "w") as current_answer:
                current_answer.write(chatgpt_answer + "\n")

            #DEBUG
            agi.verbose(chatgpt_answer,2)

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
            result = speech_synthesizer.speak_text_async(chatgpt_answer).get()
 
            stream = speechsdk.AudioDataStream(result)
            stream.save_to_wav_file(answer_path)

            # Play the recorded audio.
            agi.appexec('MP3Player', answer_path)

        else:
            agi.verbose("Error while recording: %s" % result)

    except AGIException as e:
        agi.verbose(str(e))

if __name__ == "__main__":
    main()
