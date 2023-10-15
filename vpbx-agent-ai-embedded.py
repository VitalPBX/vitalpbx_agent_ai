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
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain

# For Asterisk AGI
from asterisk.agi import *

# Load environment variables from .env file
load_dotenv("/var/lib/asterisk/agi-bin/.env")

# Retrieve environment variables
PATH_TO_DATABASE = os.environ.get('PATH_TO_DATABASE')
AZURE_SPEECH_KEY = os.environ.get('AZURE_SPEECH_KEY')
AZURE_SERVICE_REGION = os.environ.get('AZURE_SERVICE_REGION')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Uncomment if you are going to use sending information to a web page
# For valid domains with SSL:
# HOST_PORT = 'wss://valid.domain:3001'
# For environments without a valid domain:
# HOST_PORT = 'ws://IP:3001'

# Initialize Asterisk AGI
agi = AGI()

# Check if a file name and language were provided as command-line arguments
uniquedid = sys.argv[1] if len(sys.argv) > 1 else None
language = sys.argv[2] if len(sys.argv) > 1 else None

if uniquedid is None:
    print("No filename provided for the recording.")
    sys.exit(1)

# Define paths for recording, answer, previous question, and previous answer
recording_path = f"/tmp/rec{uniquedid}"
answer_path = f"/tmp/ans{uniquedid}.mp3"
pq_file = f"/tmp/pq{uniquedid}.txt"
pa_file = f"/tmp/pa{uniquedid}.txt"

# Determine the Azure language and voice settings based on the provided language
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
        # We send the 'raw' command to record the audio, 'q' for no beep, 2 seconds of silence, '30' max duration, 'y' to overwrite existing file
        sys.stdout.write('EXEC Record ' + recording_path + '.wav,2,30,y\n')
        sys.stdout.flush()
        
        # We await Asterisk's response
        result = sys.stdin.readline().strip()

        if result.startswith("200 result="):
            # Play wait message.
            agi.appexec('MP3Player', wait_message)
           
            # DEBUG
            agi.verbose("Successful Recording", 2)

            # Once everything is fine, we send the audio to OpenAI Whisper to convert it to text
            openai.api_key = OPENAI_API_KEY
            audio_file = open(recording_path + ".wav", "rb")
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
            chatgpt_question = transcript.text
            chatgpt_question_agi = chatgpt_question.replace('\n', ' ') 

            # If nothing is recorded, Whisper returns "you", so you have to ask again.
            if chatgpt_question == "you":
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

            # Find the previous question and answer for context
            if os.path.exists(pq_file):
                with open(pq_file, 'r') as previous_question_file:
                    previous_question = previous_question_file.readline().strip()
            else:
                previous_question = ""

            if os.path.exists(pa_file):
                with open(pa_file, 'r') as previous_answer_file:
                    previous_answer = previous_answer_file.readline().strip()
            else:
                previous_answer = ""

            # Initialize OpenAI components for conversation
            embeddings = OpenAIEmbeddings()
            vectordb = Chroma(persist_directory=PATH_TO_DATABASE, embedding_function=embeddings)

            # Add the previous answer and question to the conversation history
            chat_history = []

            if len(previous_question) >= 2:
                chat_history.append((previous_question, previous_answer))
                # DEBUG
                agi.verbose("PREVIOUS QUESTION OK", 2)

            # Send the question to ChatGPT
            # Low "Temperature": More deterministic and predictable responses. High "Temperature": More diverse and creative responses, but less predictable.
            
            # Create a ConversationalRetrievalChain for conversation with ChatGPT
            resp_qa = ConversationalRetrievalChain.from_llm(
                ChatOpenAI(temperature=0.2, model_name='gpt-3.5-turbo'),
                retriever=vectordb.as_retriever(search_kwargs={'k': 6}),
                return_source_documents=True,
                verbose=False
            )

            # Get the response from ChatGPT based on the user's question
            response = resp_qa(
                {"question": chatgpt_question, "chat_history": chat_history})

            chatgpt_answer = response["answer"]
            chatgpt_answer_agi = chatgpt_answer.replace('\n', ' ')

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

            # Save the current question and current answer
            with open(pq_file, "w") as current_question:
                current_question.write(chatgpt_question + "\n")

            with open(pa_file, "w") as current_answer:
                current_answer.write(chatgpt_answer + "\n")

            # Configure Azure Text-to-Speech
            speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_SERVICE_REGION)

            # Configure the output format for synthesized speech
            speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3)

            # Set the language and voice for text synthesis
            speech_config.speech_synthesis_language = azure_language 
            speech_config.speech_synthesis_voice_name = azure_voice_name

            # Create a speech synthesizer using file as audio output.
            speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
            result = speech_synthesizer.speak_text_async(chatgpt_answer).get()

            # Save the synthesized audio as a WAV file
            stream = speechsdk.AudioDataStream(result)
            stream.save_to_wav_file(answer_path)

            # Play the recorded audio.
            agi.appexec('MP3Player', answer_path)

        else:
            agi.verbose("Error while recording: %s" % result)

    except AGIException as e:
        agi.verbose("ERROR:" + str(e))

if __name__ == "__main__":
    main()
