#!/usr/bin/env python3
import sys
import os
import openai
import time

# Uncomment if you are going to use sending information to a web page
# import websockets
# import asyncio
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

# For Asterisk AGI
from asterisk.agi import *

# Load environment variables from a .env file
load_dotenv("/var/lib/asterisk/agi-bin/.env")
AZURE_SPEECH_KEY = os.environ.get('AZURE_SPEECH_KEY')
AZURE_SERVICE_REGION = os.environ.get('AZURE_SERVICE_REGION')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Uncomment if you are going to use sending information to a web page
# For valid domains with SSL:
# HOST_PORT = 'wss://valid.domain:3001'
# For environments without a valid domain:
# HOST_PORT = 'ws://IP:3001'

# Create an AGI instance
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
pq_file = f"/tmp/pq{uniquedid}.txt"
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

# Function to send a message to a WebSocket (Uncomment if needed)
# async def send_message_to_websocket(message):
#     async with websockets.connect(HOST_PORT) as websocket:
#         await websocket.send(message)

def main():
    try:
        # We send the 'raw' command to record the audio, q--> no beep, 3 seconds of silence
        sys.stdout.write('EXEC Record ' + recording_path + '.wav,3,30,y\n')
        sys.stdout.flush()

        # We await Asterisk's response
        result = sys.stdin.readline().strip()

        if result.startswith("200 result="):
            # Play wait message.
            agi.appexec('MP3Player', wait_message)

            # DEBUG
            agi.verbose("Successful Recording", 2)

            # Once everything is fine, we send the audio to OpenAI Whisper to convert it to Text
            openai.api_key = OPENAI_API_KEY
            audio_file = open(recording_path + ".wav", "rb")
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
            chatgpt_question = transcript.text
            chatgpt_question_agi = chatgpt_question.replace('\n', ' ')

            # If nothing is recorded, Whisper returns "you", so you have to ask again.
            if transcript.text == "you":
                agi.appexec('MP3Player', short_message)
                agi.verbose("Message too short", 2)
                sys.exit(1)

            # DEBUG
            agi.verbose("AUDIO TRANSCRIPT: " + chatgpt_question_agi, 2)
		
            # It is used to send the question via WebSocket, to be displayed on a web page.
            # Uncomment if you want to use this functionality with the chatserver.py script
            # If the chatserver.py program is not running the AGI will not work.
            # try:
            #     chatgpt_question_tv = "USER: " + chatgpt_question
            #     asyncio.get_event_loop().run_until_complete(send_message_to_websocket(chatgpt_question_tv))
            #     agi.verbose("MESSAGE SENT TO WEBSOCKET")
            # except AGIException as e:
            #     agi.verbose("MESSAGE SENT TO WEBSOCKET ERROR:" + str(e))
		
            # Find the previous question, with the idea of keeping the conversation
            if os.path.exists(pa_file):
                with open(pa_file, 'r') as previous_file:
                    previous_question = previous_file.readline().strip()
            else:
                previous_question = ""

            messages = []
            messages.append({"role": "user", "content": chatgpt_question})
            messages.append({"role": "assistant", "content": previous_question})
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            chatgpt_answer = response['choices'][0]['message']['content']
            chatgpt_answer_agi = chatgpt_answer.replace('\n', ' ')

            # save current question
            with open(pq_file, "w") as current_question:
                current_question.write(chatgpt_question + "\n")

            # save current answer
            with open(pa_file, "w") as current_answer:
                current_answer.write(chatgpt_answer + "\n")

            # DEBUG
            agi.verbose("ChatGPT ANSWER: " + chatgpt_answer_agi, 2)

            # It is used to send the answer via WebSocket, to be displayed on a web page.
            # Uncomment if you want to use this functionality with the chatserver.py script
            # If the chatserver.py program is not running the AGI will not work.
            # try:
            #     chatgpt_answer_tv = "ASSISTANT: " + chatgpt_answer
            #     asyncio.get_event_loop().run_until_complete(send_message_to_websocket(chatgpt_answer_tv))
            #     agi.verbose("MESSAGE SENT TO WEBSOCKET")
            # except AGIException as e:
            #     agi.verbose("MESSAGE SENT TO WEBSOCKET ERROR:" + str(e))

            # Sets API Key and Region for Azure Speech
            speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_SERVICE_REGION)

            # Sets the synthesis output format.
            # The full list of supported formats can be found here:
            # https://docs.microsoft.com/azure/cognitive-services/speech-service/rest-text-to-speech#audio-outputs
            speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3)

            # Select synthesis language and voice
            # Set either the `SpeechSynthesisVoiceName` or `SpeechSynthesisLanguage`.
            speech_config.speech_synthesis_language = azure_language
            speech_config.speech_synthesis_voice_name = azure_voice_name

            # Creates a speech synthesizer using file as audio output.
            # Replace with your own audio file
		
            # Creates a speech synthesizer using the specified speech configuration
            speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
            
            # Requests Azure Speech to convert the ChatGPT answer to speech
            result = speech_synthesizer.speak_text_async(chatgpt_answer).get()
 
            # Creates an audio stream from the result and saves it as a WAV file
            stream = speechsdk.AudioDataStream(result)
            stream.save_to_wav_file(answer_path)

            # Plays the recorded audio using MP3Player AGI application
            agi.appexec('MP3Player', answer_path)

        else:
            # If there was an error during recording, log the error
            agi.verbose("Error while recording: %s" % result)

    except AGIException as e:
        # Log any AGI-related exceptions
        agi.verbose(str(e))

if __name__ == "__main__":
    main()
