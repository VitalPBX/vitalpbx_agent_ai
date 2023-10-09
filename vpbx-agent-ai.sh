#!/bin/bash
# This code is the property of VitalPBX LLC Company
# License: Proprietary
# Date: 9-Oct-2023
# VitalPBX Agent AI with ChatGPT(Embedded), Whisper and Azure Speech(TTS)
#
set -e
cd /var/lib/asterisk/agi-bin/
mkdir /var/lib/asterisk/agi-bin/docs
mkdir /var/lib/asterisk/agi-bin/data
wget https://raw.githubusercontent.com/VitalPBX/vitalpbx_agent_ai_chatgpt/main/chatbot.py /var/lib/asterisk/agi-bin/
wget https://raw.githubusercontent.com/VitalPBX/vitalpbx_agent_ai_chatgpt/main/record-prompt.py /var/lib/asterisk/agi-bin/
wget https://raw.githubusercontent.com/VitalPBX/vitalpbx_agent_ai_chatgpt/main/vpbx-agent-ai-embeded.py /var/lib/asterisk/agi-bin/
wget https://raw.githubusercontent.com/VitalPBX/vitalpbx_agent_ai_chatgpt/main/vpbx-agent-ai.py /var/lib/asterisk/agi-bin/
wget https://raw.githubusercontent.com/VitalPBX/vitalpbx_agent_ai_chatgpt/main/vpbx-embeded-docs.py /var/lib/asterisk/agi-bin/
chmod +x /var/lib/asterisk/agi-bin/chatbot.py
chmod +x /var/lib/asterisk/agi-bin/record-prompt.py
chmod +x /var/lib/asterisk/agi-bin/vpbx-agent-ai-embeded.py
chmod +x /var/lib/asterisk/agi-bin/vpbx-agent-ai.py
chmod +x /var/lib/asterisk/agi-bin/vpbx-embeded-docs.py
wget https://raw.githubusercontent.com/VitalPBX/vitalpbx_agent_ai_chatgpt/main/extensions__70-agent-ai.conf /etc/asterisk/vitalpbx/
