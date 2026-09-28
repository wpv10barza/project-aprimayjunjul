#!/bin/bash
# _tmux_piper_export.sh
# builds a complete piper voice with the help of textymcspeechy-piper Docker container
# this version updates the .onnx.json data to produce piper compliant models.

checkpoint="$1"
destination="$2"
dojo_name="$3"

DATASET_CONF_FILE="../target_voice_dataset/dataset.conf"
QUALITY_FILE="../target_voice_dataset/.QUALITY"
quality=""

if [[ -f $QUALITY_FILE ]]; then
    QUALITY_CODE=$(cat $QUALITY_FILE)
else
    echo "Error: .QUALITY file not found."
    exit 1
fi

if [ -e $DATASET_CONF_FILE ]; then
    source $DATASET_CONF_FILE
else
    echo "$0 - dataset.conf not found"
    echo "     expected location: $DATASET_CONF_FILE"
    echo 
    exit 1
fi

if [ "$QUALITY_CODE" = "L" ]; then
    quality="low"
elif [ "$QUALITY_CODE" = "M" ]; then
    quality="medium"
elif [ "$QUALITY_CODE" = "H" ]; then
    quality="high" 
else 
    echo "Error - invalid value for quality: $QUALITY_CODE"
    exit 1
fi

SETTINGS_FILE="SETTINGS.txt"
if [ -e $SETTINGS_FILE ]; then
    source $SETTINGS_FILE
else
    echo "$0 - settings not found"
    echo "     expected location: $SETTINGS_FILE"
    echo 
    echo "press <enter> to exit"
    exit 1
fi

update_json() {
    local language_code="$1"
    local quality="$2"
    local filename="$3"
    local dataset_name=$(basename "$filename" .onnx.json)
    jq --arg lang_code "$language_code" \
       --arg quality_value "$quality" \
       --arg dataset "$dataset_name" \
       '.audio.quality = $quality_value |
        .language.code = $lang_code |
        .dataset = $dataset' \
       "$filename" > tmp.json && mv tmp.json "$filename" && chown 1000:1000 "$filename"
}

create_piper_voice(){
    container_checkpoint=/app/tts_dojo/${dojo_name}/$(dirname "$checkpoint" | xargs basename)/$(basename "$checkpoint")
    container_destination=/app/tts_dojo/${dojo_name}/tts_voices/$(dirname "$destination" | xargs basename)/$(basename "$destination")
    docker exec textymcspeechy-piper bash -c "cd /app/piper/src/python && python3 -m piper_train.export_onnx $container_checkpoint $container_destination" 
    cp ../training_folder/config.json "$destination.json"
    update_json "$PIPER_FILENAME_PREFIX" "$quality" "$destination.json"
}

echo "Checkpoint exporting to ONNX"
echo "checkpoint  = $checkpoint"
echo "destination = $destination"
echo "dojo_name   = $dojo_name"
time_output=$( (time create_piper_voice) 2>&1 )
echo "Done!"
real_time=$(echo "$time_output" | grep real | awk '{print $2}')
minutes=$(echo "$real_time" | grep -oP '^\d+(?=m)')
seconds=$(echo "$real_time" | grep -oP '(?<=m)\d+(\.\d+)?s' | sed 's/s//')
if [ -z "$minutes" ]; then minutes=0; fi
seconds_precise=$(echo "$minutes * 60 + $seconds" | bc)
seconds_int=$(printf "%.0f" "$seconds_precise")
$(echo $seconds_int > $EXPORTER_LAST_EXPORT_SECONDS_FILE)
