# VitalPBX - AI Agent with OpenAI ChatGPT, Whisper and Microsoft Azure AI Speech (TTS)
## Necessary Resources
1.	OpenAI Account (https://platform.openai.com/apps).
2.	Microsoft Azure Account (https://azure.microsoft.com/en-us/products/ai-services/text-to-speech)
3.	VitalPBX 4

## Installing dependencies
<pre>
  apt update
  apt install python3 python3-pip
  pip install azure-cognitiveservices-speech
  pip install pyst2
</pre>

<pre>
  wget https://raw.githubusercontent.com/VitalPBX/vitalpbx_agent_ai_chatgpt/main/requirements.txt
</pre>

<pre>
  pip install -r requirements.txt
</pre>

## Install from script
Download the script
<pre>
  wget https://raw.githubusercontent.com/VitalPBX/vitalpbx_agent_ai_chatgpt/main/vpbx-agent-ai.sh
</pre>

Give execution permissions
<pre>
  chmod +x vpbx-agent-ai.sh
</pre>

Run the script
<pre>
  ./vpbx-agent-ai.sh
</pre>

## Create .env file
Goto AGI directory
<pre>
  cd /var/lib/asterisk/agi-bin/
</pre>

Creating .env
<pre>
  nano .env
</pre>

Copy the following content and add the APIS Key.
<pre>
OPENAI_API_KEY = "sk-"
AZURE_SPEECH_KEY = ""
AZURE_SERVICE_REGION = "eastus"
PATH_TO_DOCUMENTS = "/var/lib/asterisk/agi-bin/docs/"
PATH_TO_DATABASE = "/var/lib/asterisk/agi-bin/data/"
</pre>

## Create voice guides
Goto AGI directory
<pre>
  cd /var/lib/asterisk/agi-bin/
</pre>

The format to record a prompt is as follows:
./record-prompt.py <strong>file-name "Text to record" language</strong><br>
<strong>file-name</strong> --> file name if extension mp3, remember that in the Agent AI script, the welcome audio is: welcome-en (English), welcome-es (Spanish), and the wait audio is: wait-en (English), and wait-es (Spanish).<br>
<strong>languaje</strong> --> could be "en-US" or "es-ES"<br>
If you want to add more languages, you must modify the scripts<br>

Below we show an example of how you should use the script to record the prompt.
<pre>
./record-prompt.py wait-en "wait a moment" "en-US"
./record-prompt.py welcome-en "Thanks for calling, I'm Vicky, your AI assistant, how can I help you today?" "en-US"
./record-prompt.py short-message-en "The question is too short, please try again" "en-US"
./record-prompt.py wait-es "espere un momento" "es-ES"
./record-prompt.py welcome-es "Gracias por llamar, soy Vicky, tu asistente, en que te puedo ayudar hoy?" "es-ES"
./record-prompt.py short-message-es "La pregunta es demasiado corta, intente de nuevo por favor" "es-ES"
</pre>

## Testing Embedding
To test the functionality of our AI Agent with the Embedding option, run the following script:<br>
1.- Upload the document to the /var/lib/asterisk/agi-bin/docs folder with the information to use for the query with ChatGPT-Embedded<br>
2.- To transfer this document to a Vector database (ChromaDB), proceed to execute the following command.
<pre>
  cd /var/lib/asterisk/agi-bin/
  ./vpbx-embedded-docs.py
</pre>
3.- Now execute the following command and we proceed to ask any question in reference to the document that we previously uploaded.
<pre>
  cd /var/lib/asterisk/agi-bin
  ./chatbot.py
</pre>

## Testing call from VitalPBX
To ask ChatGPT questions: Dial *778 for English or *779 for Spanish<br>
For queries obtained from custom documentation, first upload the PDF document in the docs folder, then run from the console the command:
<pre>
  cd /var/lib/asterisk/agi-bin/ 
  ./vpbx-embedded-docs.py
</pre>
To ask ChatGPT-Embedded questions: Dial *888 for English or *889 for Spanish
