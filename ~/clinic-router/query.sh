#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
PROMPT=$(cat router_prompt.txt)
USER_MSG="$*"

# Ollama prompt formatı: SYSTEM + USER
ollama run gemma2:2b <<EOF
SYSTEM:
$PROMPT

USER:
$USER_MSG
EOF
