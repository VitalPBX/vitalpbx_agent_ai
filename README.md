# VitalPBX - AI Agent with OpenAI ChatGPT, Whisper and Microsoft Azure AI Speech (TTS)
![VitalPBX AGENT AI](https://github.com/VitalPBX/vitalpbx_agent_ai_chatgpt/blob/main/vpbx_agent_ai.png)
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
  pip install pydub
  pip install python-dotenv==0.21.0
  pip install langchain==0.0.331rc2
  pip install pypdf==3.8.1
  pip install docx2txt==0.8
  pip install openai
  pip install chromadb==0.3.22
  pip install tiktoken==0.4.0
  pip install markdown
</pre>

## Install from script
Download the script
<pre>
  wget https://raw.githubusercontent.com/VitalPBX/vitalpbx_agent_ai_chatgpt/main/install.sh
</pre>

Give execution permissions
<pre>
  chmod +x install.sh
</pre>

Run the script
<pre>
  ./install.sh
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
./record-prompt.py wait-en "Just a moment, please. We're fetching the information for you." "en-US"
./record-prompt.py welcome-en "Welcome to the Artificial intelligence Assistant. Please ask your question after the tone." "en-US"
./record-prompt.py short-message-en "Your question is too short. Please provide more details." "en-US"
./record-prompt.py anything-else-en "Can I assist you with anything else?" "en-US"  
./record-prompt.py wait-es "Un momento, por favor. Estamos buscando la información para ti." "es-ES"
./record-prompt.py welcome-es "Bienvenido al Asistente de Inteligencia Artificial, Haga su pregunta después del tono." "es-ES"
./record-prompt.py short-message-es "Tu pregunta es demasiado corta. Por favor, proporciona más detalles." "es-ES"
./record-prompt.py anything-else-es "¿Hay algo más en lo que pueda ayudarte?" "es-ES"  
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

## View in real time
It is possible to see the question and answer in real time on a web page, for which we are going to follow the following procedure.<br>

Install prerequisites
<pre>
pip install websocket-client
pip install asyncio
</pre>

We are going to copy the chatserver.py file to the folder we want (It could be /var/lib/asterisk/agi-bin/).
<pre>
  cd /var/lib/asterisk/agi-bin/
  wget https://raw.githubusercontent.com/VitalPBX/vitalpbx_agent_ai_chatgpt/main/chatserver.py
  chamod +x chatserver.py
</pre>

Edit the file you just downloaded (chatserver.py)
<pre>
  cd /var/lib/asterisk/agi-bin/
  nano chatserver.py
</pre>

Replace the following lines with your IP or Domain if you use SSL.<br>
If you use ssl with a valid domain remember to change ws to wss.
<pre>
start_server = websockets.serve(echo, 'Your_IP_or_Domain', 3001)
print("WebSocket server started on ws://Your_IP_or_Domain:3001")
</pre>

Now we will proceed to create the service
<pre>
  cd /etc/systemd/system/
  nano vpbxagentai.service
</pre>

Copy and paste the following content
<pre>
[Unit]
Description=Agent AI
After=network.target

[Service]
ExecStart=/usr/bin/python3 /var/lib/asterisk/agi-bin/chatserver.py
Restart=always
User=root
Group=root
Environment=VariableDeEntorno=valor
WorkingDirectory=/var/lib/asterisk/agi-bin

[Install]
WantedBy=multi-user.target
</pre>

Enable and start the service
<pre>
systemctl enable vpbxagentai
systemctl start vpbxagentai
systemctl status vpbxagentai
</pre>

Now we are going to download the chat.html file and copy it to the /usr/share/vitalpbx/www folder
<pre>
  cd /usr/share/vitalpbx/www
  mkdir chatview
  cd chatview
  wget https://raw.githubusercontent.com/VitalPBX/vitalpbx_agent_ai_chatgpt/main/chatview/index.html
  wget https://raw.githubusercontent.com/VitalPBX/vitalpbx_agent_ai_chatgpt/main/chatview/vpbx-agent-ai-m.png
</pre>
For HTTPS: wss, for HTTP: ws. If you are not going to use SSL just enter the IP of your server, otherwise leave ${location.hostname}.<br>

Finally, edit the files vpbx-agent-ai-embedded.py and vpbx-agent-ai.py and uncomment everything related to sending messages via websocket.<br>

To see the chat in real time, run the url of your VitalPBX:<br>
For example:<br>
http://mypbxurl/chatview<br>
or<br>
https://mypbxurl/chatview

### Note
Remember to unblock port 3001 or the one you decided to use in the VitalPBx firewall as in any other firewall that VitalPBX has in front of you.<br>
To make sure everything is fine, we can run the following command.
<pre>
  netstat -tuln | grep 3001
</pre>
And it would have to return the following to us:
<pre>
tcp        0      0 192.168.57.50:3001       0.0.0.0:*               LISTEN     
tcp        0      0 127.0.1.1:3001           0.0.0.0:*               LISTEN  
</pre>
192.168.57.50 is our public or private IP.
