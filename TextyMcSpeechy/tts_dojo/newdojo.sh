#!/bin/bash
# newdojo.sh - creates and configures a new dojo for training piper voice models

set -e # abort script on all errors

RESET='\033[0m'
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'

if [ -z "$1" ]; then
  echo
  echo
  echo "Usage: $0 <VOICE_NAME>"
  echo "  Please supply a name for the voice being created."
  echo "  Training environment will be created in <VOICE_NAME>_dojo"
  echo
  echo "Exiting."
  echo
  exit 1
fi

VOICE_NAME="$1"
DIRECTORY="${VOICE_NAME}_dojo"

if [ -d "$DIRECTORY" ]; then
  echo "Error: Directory '$DIRECTORY' already exists."
  exit 1
fi

mkdir "$DIRECTORY"

echo
echo "Dojo created in : '$PWD/$DIRECTORY'"
echo "Populating with : '$PWD/DOJO_CONTENTS'"
cp -r ./DOJO_CONTENTS/* ./$DIRECTORY

echo "Setting proper permissions on: '$PWD/$DIRECTORY'"
chown -R 1000:1000 ./$DIRECTORY

echo
echo -e "  Dojo is ready! You will find it here:  ${CYAN}${DOJO_DIR}${RESET}"
echo
echo -e "  use ${YELLOW}run_training.sh${RESET} inside your new dojo to guide you through the training process"
echo
echo
exit 0
