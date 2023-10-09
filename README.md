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
  apt install -r requirements.txt
</pre>

## Install from script

<pre>
  wget
</pre>

Dar permisos de ejecucion
<pre>
  chmod +x vpbx-agent-ai.sh
</pre>

Ejecutar
<pre>
  ./vpbx-agent-ai.sh
</pre>

## Create .env file
<pre>
  nano .env
</pre>

Copy the following content and add the APP Key to them and configure the routes correctly.
<pre>
OPENAI_API_KEY = "sk-"
AZURE_SPEECH_KEY = ""
AZURE_SERVICE_REGION = "eastus"
PATH_TO_DOCUMENTS = "/var/lib/asterisk/agi-bin/docs/"
PATH_TO_DATABASE = "/var/lib/asterisk/agi-bin/data/"
</pre>

