#!/bin/bash
# Script to batch remove room tone / background noise from a set of wav files.
# Requires a short wav sample of the quiet background noise in the environment where your dataset was recorded.
#
#   If using the TextyMcspeechy dataset recorder,  
#   the easiest way to acquire this sample is to add the following line at the beginning of your metadata.csv: (remove initial # and spaces)
#
#   roomtone|(record 10-20 seconds of silence for noise reduction purposes)
#

# Usage:
#   ./script.sh <input_directory> <output_directory> [--roomtonepath <room_tone_file>]

if ! command -v sox &> /dev/null; then
    echo "This tool requires sox, which is not installed on your system"
    echo "To install:"
    echo " Ubuntu/Debian:    sudo apt install sox"
    echo " Fedora/RHEL:      sudo dnf install sox"
    echo " Arch Linux:       sudo pacman -S sox"
    echo " macOS (Homebrew): brew install sox"
    echo
    echo "After installing, run this script again."
    exit 1
fi

show_usage() {
  echo "Usage:"
  echo "  ./remove_roomtone.sh <input_directory> <output_directory> [--roomtonepath <room_tone_wavfile>]"
  echo "Arguments:"
  echo "  input_directory   Directory containing your dataset's WAV files"
  echo "  output_directory  Directory to save WAV files with background noise removed"
  echo "  --roomtonepath    Path to a WAV recording of the background noise in the room where the dataset was recorded."
  echo "                    If not provided, the script checks ./roomtone.wav"
}

input_dir=""
output_dir=""
room_tone="./roomtone.wav"

if [[ $# -lt 2 ]]; then
  show_usage
  exit 1
fi

input_dir="$1"
output_dir="$2"
shift 2

while [[ $# -gt 0 ]]; do
  case "$1" in
    --roomtonepath)
      if [[ -z "$2" || "$2" == "--"* ]]; then
        echo "Error: Missing value for --roomtonepath"
        show_usage
        exit 1
      fi
      room_tone="$2"
      shift 2
      ;;
    *)
      echo "Error: Unknown argument $1"
      show_usage
      exit 1
      ;;
  esac
done

if [[ ! -d "$input_dir" ]]; then
  echo "Error: Input directory '$input_dir' does not exist."
  show_usage
  exit 1
fi

mkdir -p "$output_dir"

if [[ ! -f "$room_tone" ]]; then
  echo "Error: Room tone file '$room_tone' not found."
  show_usage
  exit 1
fi

noise_profile="noise.prof"
if [[ ! -f "$noise_profile" ]]; then
  echo "Generating noise profile from $room_tone..."
  sox "$room_tone" -n noiseprof "$noise_profile"
fi

process_file() {
  local input_file="$1"
  local output_file="$2"
  echo "Processing: $input_file -> $output_file"
  sox "$input_file" "$output_file" noisered "$noise_profile" 0.21
}

for wav_file in "$input_dir"/*.wav; do
  if [[ -f "$wav_file" ]]; then
    base_name=$(basename "$wav_file")
    output_file="$output_dir/$base_name"
    process_file "$wav_file" "$output_file"
  fi
done

echo "Noise removal completed. Cleaned files are in: $output_dir"
