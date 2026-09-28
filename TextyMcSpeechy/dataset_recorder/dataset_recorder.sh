#!/bin/bash

RESET='\033[0m'
BLACK='\033[0;30m'
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[0;37m'
BOLD_BLACK='\033[1;30m'
BOLD_RED='\033[1;31m'
BOLD_GREEN='\033[1;32m'
BOLD_YELLOW='\033[1;33m'
BOLD_BLUE='\033[1;34m'
BOLD_PURPLE='\033[1;35m'
BOLD_CYAN='\033[1;36m'
BOLD_WHITE='\033[1;37m'
OUTPUT_DIR=wav
output_dir=""
declare -a filenames=()
declare -a phrases=()
declare -a recorded=()
no_recording_index="0"

cleanup(){
  echo "cleaning up processes"
  stty echo
  sleep 1
  stop_arecord
  tput cnorm
  sleep 1
  exit 1
}

center_text() { 
    COLUMNS=$(tput cols)
    printf "%*s\n" $(( ( $(echo $* | wc -c ) + COLUMNS ) / 2 )) "$*"
}

justify_text() {
    local width=$1
    local text=$2
    COLUMNS=$(tput cols)
    text=$(printf "%-${width}s" "$text")
    printf "%*s\n" $(( ( ${#text} + COLUMNS ) / 2 )) "$text"
}

check_files() {
    for ((i = 0; i < ${#filenames[@]}; i++)); do
        thisfile=false
        path="$output_dir/${filenames[i]}"
        if [[ -f "$path" ]]; then
            recorded[i]=true
            thisfile=true
        else
           recorded[i]=false
           thisfile=false
        fi
        if [ "$no_recording_index" = "0" ] && [ "$thisfile" = "false" ]; then 
            no_recording_index=$((i-1))
        fi
    done
}

original_tty_settings=""
hide_terminal_output() { tput civis; stty -echo; }
restore_terminal_output() { stty echo; tput cnorm; }

trim_wav() {
    local input_file="$1"
    if [ ! -f "$input_file" ]; then
        echo "Error: File '$input_file' not found."
        return 1
    fi
    temp_file="/tmp/trimmed.wav"
    duration=$(ffprobe -i "$input_file" -show_entries format=duration -v quiet -of csv="p=0")
    new_duration=$(awk "BEGIN {printf \"%.3f\", $duration - 0.1}")
    ffmpeg -y -i "$input_file" -ss 00:00:00.050 -t "$new_duration" -c copy "$temp_file" >/dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "Error: Failed to trim '$input_file'."
        return 1
    fi
    rm $input_file 
    cp "$temp_file" "$input_file"
    rm "$temp_file"
}

stop_arecord() {
    if [[ -n "$arecord_pid" ]]; then
        kill "$arecord_pid" >/dev/null 2>&1
    fi
}

load_metadata() {
    local csv_file=${1:-"metadata.csv"}
    local line_number=0
    while IFS='|' read -r col1 col2 _; do
        if [ -z "$col1" ] || [ -z "$col2" ]; then break; fi
        ((line_number++))
        index=$((line_number - 1))
        filename="${col1}.wav"
        phrase="${line_number}. ${col2}"
        filenames+=("$filename")
        phrases+=("$phrase")
        recorded+=false
    done < "$csv_file"
}

output_recorded() { echo "Recorded array:"; printf '%s\n' "${recorded[@]}"; }
output_filenames() { echo "Filenames array:"; printf '%s\n' "${filenames[@]}"; }
output_phrases() { echo "Phrases array:"; printf '%s\n' "${phrases[@]}"; }
get_phrase(){ local phrase=${phrases[$index]}; echo "$phrase"; }
get_filename(){ local filename=${filenames[$index]}; echo "$filename"; }

record_wav() {
    local filename=$(get_filename)
    update_display "Recording - press [r] to stop."
    arecord -f cd -t wav -d 30 -r 44100 "$output_dir"/"$filename" > /dev/null 2>&1 &
    arecord_pid=$!
    while true; do
        read -r -n 1 keypress
        if [[ "$keypress" == [rR] ]]; then
            stop_arecord
            recorded[index]=true
            trim_wav "$output_dir"/"$filename" "100"
            break
        fi
    done
}

listen_to_wav() { local filename=$(get_filename); aplay "$output_dir/$filename" >/dev/null 2>&1; }
show_item(){ local phrase="$(get_phrase $index)"; center_text "$phrase"; }

show_legend(){
   echo -e "${YELLOW}"
   local has_audio=${recorded[index]}
   if [ "$index" -lt $((arraylength)) ]; then
       if [ "$index" -ge "0" ]; then justify_text 20 "[r]ecord"; fi
       if [ "$index" -gt "0" ]; then justify_text 20 "[p]revious"; fi
       if [ "$has_audio" = "true" ]; then
               justify_text 20 "[n]ext"
               justify_text 20 "[l]isten to saved"
       fi
       justify_text 20 "[q]uit"
       echo -e "${RESET}"
  else
       center_text "End of dataset."
       echo; echo
       justify_text 20 "[q]uit"
       justify_text 20 "[p]revious"
       justify_text 20 "[g]o to start"
  fi
}

update_display() {
    legendinput="$1"
    echo "legendinput = $legendinput"
    clear
    echo -e "\n\n\n\n\n\n\n\n\n\n"
    show_item
    echo -e "\n\n\n\n"
    if [ -z "$legendinput" ]; then show_legend; else justify_text 20 "$legendinput"; fi
}

trap cleanup SIGINT SIGTERM
csv_file="${1:-metadata.csv}"
output_dir="${2:-$OUTPUT_DIR}"
load_metadata $csv_file
check_files
index=0
clear
echo -e "\n\n\n\n\n\n\n"
center_text "Texty Mcspeechy speedy dataset recorder"
echo
center_text "Painlessly record a dataset for any 'metadata.csv' file"

if [ -n $1 ]; then
    center_text "Recording dataset for your csv file : $1"
else
    center_text "optional usage: ./dataset_recorder.sh [<your_metadata.csv>]  [<directory for recordings>]"
fi
echo; echo
center_text "press <ENTER>"
read
update_needed=true
if [ $no_recording_index -gt 0 ]; then
    clear
    echo -e "\n\n\n\n\n"
    center_text "Files from a previous session exist in directory \"$output_dir\""
    echo
    center_text "Would you like to:"
    justify_text 20 "  [D]elete files and start over"
    justify_text 20 "  [C]ontinue where you left off"
    read choice
    if [ $choice = "d" ] || [ $choice = "D" ]; then
        rm "$output_dir/*.wav"
        $no_recording_index=0
        index=$no_recording_index
    elif [ $choice = "c" ] || [ $choice = "C" ]; then
        echo "Continuing."
        index=$no_recording_index
    fi     
else
    index=0
fi
hide_terminal_output
arraylength=${#filenames[@]}

while true; do
  if [ "$update_needed" = "true" ]; then
    update_display
    update_needed=false
  fi
  read -r -n 1 keypress
  case "$keypress" in
        r|R)
            if [ $index -lt $((arraylength )) ]; then 
                record_wav $index
                index=$((index + 1))
                update_needed=true
            fi
            ;;
        p|P)
            if [ $index -ge 1 ]; then index=$((index -1)); update_needed=true; fi
            ;;
        l|L) listen_to_wav ;;
        n|N)
            has_audio=${recorded[index]}
            echo 
            if [ $index -lt $arraylength ] && [ "$has_audio" = "true" ]; then index=$((index +1)); update_needed=true; fi
            ;;
        q|Q) restore_terminal_output; exit 0 ;;
        *) : ;;
  esac
done
