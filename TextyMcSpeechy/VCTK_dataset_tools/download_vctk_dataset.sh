#!/bin/bash

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

if command_exists unzip; then
    echo "Unzip is installed."
else
    echo "Unzip is not installed."
    if [[ -f /etc/debian_version ]]; then
        echo "To install unzip, you can run the following command:"
        echo "sudo apt update && sudo apt install unzip"
    elif [[ -f /etc/redhat-release ]]; then
        echo "To install unzip, you can run the following command:"
        echo "sudo yum install unzip"
    elif [[ "$(uname)" == "Darwin" ]]; then
        echo "To install unzip on macOS, use Homebrew:"
        echo "brew install unzip"
    else
        echo "Please consult your system's documentation to install unzip."
    fi
fi

EXPECTED_FILE_SIZE=11747302977

if [[ -f "VCTK-Corpus-0.92.zip" && $(stat -c%s "VCTK-Corpus-0.92.zip") -eq $EXPECTED_FILE_SIZE ]]; then
    echo "VCTK-Corpus-0.92.zip is already downloaded."
else
    echo "About to download VCTK dataset. Warning! This is a very large file (~11GB)."
    read -p "Do you want to proceed with the download? (y/n): " response
    response=${response,,}
    if [[ "$response" == "y" || "$response" == "yes" ]]; then
        echo "Starting download..."
        wget https://datashare.ed.ac.uk/bitstream/handle/10283/3443/VCTK-Corpus-0.92.zip
        echo "Download complete."
    else
        echo "Download aborted."
        exit 0
    fi
fi

echo
read -p "Corpus must be unzipped before use. Do you want to unzip now? (y/n): " response2
response2=${response2,,}

if [[ "$response2" == "y" || "$response2" == "yes" ]]; then
    if [[ -f "VCTK-Corpus-0.92.zip" ]]; then
        echo "Unzipping the corpus to VCTK-Corpus-0.92..."
        mkdir ./VCTK-Corpus-0.92
        unzip VCTK-Corpus-0.92.zip -d ./VCTK-Corpus-0.92
        echo "Unzipping complete."
    else
        echo "Error: VCTK-Corpus-0.92.zip was not found."
    fi
else
    echo "Exiting."
fi
