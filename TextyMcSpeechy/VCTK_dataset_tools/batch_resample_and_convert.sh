#!/bin/bash

COMMON_SAMPLE_RATES=(16000 22050 32000 40000 44100 48000)
DEFAULT_OUTPUT_FORMAT=""

if [ "$#" -lt 3 ]; then
  echo
  echo "Usage: $0 <input_dir> <output_dir> <sampling_rate> [--output_format <flac|wav>]"
  echo
  exit 1
fi

INPUT_DIR="$1"
OUTPUT_DIR="$2"
TARGET_RATE="$3"

if [ "$#" -eq 5 ] && [ "$4" == "--output_format" ]; then
  OUTPUT_FORMAT="$5"
  if [[ "$OUTPUT_FORMAT" != "flac" && "$OUTPUT_FORMAT" != "wav" ]]; then
    echo "Error: Invalid output format '$OUTPUT_FORMAT'. Use 'flac' or 'wav'."
    exit 1
  fi
else
  OUTPUT_FORMAT=""
fi

if [ ! -d "$INPUT_DIR" ]; then
  echo "Error: '$INPUT_DIR' is not a valid directory"
  exit 1
fi
mkdir -p "$OUTPUT_DIR"

if ! [[ " ${COMMON_SAMPLE_RATES[@]} " =~ " ${TARGET_RATE} " ]]; then
  echo
  echo "Error: The sampling rate $TARGET_RATE is not commonly used. Please choose from: ${COMMON_SAMPLE_RATES[*]}"
  echo
  exit 1
fi

input_files=($(find "$INPUT_DIR" -maxdepth 1 -type f \( -name '*.wav' -o -name '*.flac' \) -not -name '.*'))
total_files=${#input_files[@]}
echo
echo "Found $total_files audio files in '$INPUT_DIR' to be converted."

file_count=0
for file in "${input_files[@]}"; do
  file_count=$((file_count + 1))
  filename=$(basename -- "$file")
  extension="${filename##*.}"
  if [[ -z "$OUTPUT_FORMAT" ]]; then OUTPUT_FORMAT="$extension"; fi
  echo "Processing file $file_count of $total_files: $filename"
  base_filename="${filename%.*}"
  output_file="$OUTPUT_DIR/$base_filename.$OUTPUT_FORMAT"
  if ! ffmpeg -i "$file" -ar "$TARGET_RATE" "$output_file" > /dev/null 2>&1; then
    echo "Error converting $filename"
  fi
done

echo
echo "Conversion complete. Your converted files were created in the '$OUTPUT_DIR' directory."
