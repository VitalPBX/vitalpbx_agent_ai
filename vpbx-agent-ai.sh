#!/bin/bash
# This code is the property of VitalPBX LLC Company
# License: Proprietary
# Date: 9-Oct-2023
# VitalPBX Agent AI with ChatGPT(Embedded), Whisper and Azure Speech(TTS)
#
set -e
echo -e "************************************************************"
echo -e "*          Welcome to the AI Agent installation            *"
echo -e "************************************************************"
cd /var/lib/asterisk/agi-bin/
mkdir /var/lib/asterisk/agi-bin/docs
mkdir /var/lib/asterisk/agi-bin/data
wget https://raw.githubusercontent.com/VitalPBX/vitalpbx_agent_ai_chatgpt/main/chatbot.py -P /var/lib/asterisk/agi-bin/
wget https://raw.githubusercontent.com/VitalPBX/vitalpbx_agent_ai_chatgpt/main/record-prompt.py -P /var/lib/asterisk/agi-bin/
wget https://raw.githubusercontent.com/VitalPBX/vitalpbx_agent_ai_chatgpt/main/vpbx-agent-ai-embedded.py -P /var/lib/asterisk/agi-bin/
wget https://raw.githubusercontent.com/VitalPBX/vitalpbx_agent_ai_chatgpt/main/vpbx-agent-ai.py -P /var/lib/asterisk/agi-bin/
wget https://raw.githubusercontent.com/VitalPBX/vitalpbx_agent_ai_chatgpt/main/vpbx-embedded-docs.py -P /var/lib/asterisk/agi-bin/
chmod +x /var/lib/asterisk/agi-bin/chatbot.py
chmod +x /var/lib/asterisk/agi-bin/record-prompt.py
chmod +x /var/lib/asterisk/agi-bin/vpbx-agent-ai-embedded.py
chmod +x /var/lib/asterisk/agi-bin/vpbx-agent-ai.py
chmod +x /var/lib/asterisk/agi-bin/vpbx-embedded-docs.py
wget https://raw.githubusercontent.com/VitalPBX/vitalpbx_agent_ai_chatgpt/main/extensions__70-agent-ai.conf -P /etc/asterisk/vitalpbx/
asterisk -rx"dialplan reload"
echo -e "\n"
echo -e "************************************************************"
echo -e "*       All components have been installed correctly       *"
echo -e "*                To ask ChatGPT questions                  *"                  
echo -e "*        Dial *778 for English or *779 for Spanish         *"
echo -e "*     For queries obtained from custom documentation       *"
echo -e "*    First upload the PDF document in the docs folder      *"
echo -e "*         Then run from the console the command:           *"
echo -e "*                ./vpbx-embedded-docs.py                   *"
echo -e "*            To ask ChatGPT-Embedded questions             *"                  
echo -e "*        Dial *888 for English or *889 for Spanish         *"
echo -e "************************************************************"
