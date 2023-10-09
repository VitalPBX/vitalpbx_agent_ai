#!/bin/bash
# This code is the property of VitalPBX LLC Company
# License: Proprietary
# Date: 9-Oct-2023
# VitalPBX Agent AI with ChatGPT(Embedded), Whisper and Azure Speech(TTS)
#
set -e
cd /var/lib/asterisk/agi-bin/
mkdir docs
mkdir data
wget https://raw.githubusercontent.com/VitalPBX/vitalpbx_agent_ai_chatgpt/main/chatbot.py
wget https://raw.githubusercontent.com/VitalPBX/vitalpbx_agent_ai_chatgpt/main/record-prompt.py
wget https://raw.githubusercontent.com/VitalPBX/vitalpbx_agent_ai_chatgpt/main/vpbx-agent-ai-embeded.py
wget https://raw.githubusercontent.com/VitalPBX/vitalpbx_agent_ai_chatgpt/main/vpbx-agent-ai.py
wget https://raw.githubusercontent.com/VitalPBX/vitalpbx_agent_ai_chatgpt/main/vpbx-embeded-docs.py
chmod +x chatbot.py
chmod +x record-prompt.py
chmod +x vpbx-agent-ai-embeded.py
chmod +x vpbx-agent-ai.py
chmod +x vpbx-embeded-docs.py


wget https://raw.githubusercontent.com/VitalPBX/vitalpbx_agent_ai_chatgpt/main/extensions__70-agent-ai.conf
