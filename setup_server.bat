@echo off
title The Grand Knox - Server Provisioner
chcp 65001 > nul
echo ==============================================================================
echo                 COMMENCING ONE-CLICK DISCORD SERVER PROVISIONING             
echo ==============================================================================
python run_setup_standalone.py
pause
