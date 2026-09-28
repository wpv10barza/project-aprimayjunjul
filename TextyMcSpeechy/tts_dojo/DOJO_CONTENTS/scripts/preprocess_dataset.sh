#!/bin/bash
#preprocess_dataset.sh:   Configures and runs piper_train.preprocess inside the textymcspeechy-piper docker container

DOJO_NAME=$(basename $PWD)
SETTINGS_FILE="SETTINGS.txt"
CACHE_DIR="../training_folder/cache"
CONFIG_JSON="../training_folder/config.json"
DATASET_JSONL="../training_folder/dataset.jsonl"
SAMPLING_RATE_FILE=".SAMPLING_RATE"
MAX_WORKERS_FILE=".MAX_WORKERS"
MASTER_SETTINGS_FILE="../../DOJO_CONTENTS/scripts/$SETTINGS_FILE"
DATASET_CONF_FILE="../target_voice_dataset/dataset.conf" 

cd scripts
set +e

if [[ -f $SAMPLING_RATE_FILE ]]; then
    SAMPLING_RATE=$(cat $SAMPLING_RATE_FILE)
else
    echo "Error: .SAMPLING_RATE file not found."
    exit 1 
fi

if [[ -f $MAX_WORKERS_FILE ]]; then
    MAX_WORKERS=$(cat $MAX_WORKERS_FILE)
else
    echo "Error: .MAX_WORKERS file not found."
    exit 1
fi

if [ -e $DATASET_CONF_FILE ]; then
    source $DATASET_CONF_FILE
else
    echo "$0 - dataset.conf not found"
    echo "     expected location: $DATASET_CONF_FILE"
    echo 
    echo "press <enter> to exit"
    exit 1
fi

missing=false
if [[ -z "$ESPEAK_LANGUAGE_IDENTIFIER" ]]; then
    echo
    echo
    echo "    Error: ESPEAK_LANGUAGE_IDENTIFIER is not set in dataset.conf."
    missing=true
fi

if [[ -z "$PIPER_FILENAME_PREFIX" ]]; then
    echo "    Error: PIPER_FILENAME_PREFIX is not set in dataset.conf."
    echo
    missing=true
fi

if [[ "$missing" == true ]]; then
    echo
    echo "    Your dataset configuration file (dataset.conf) is outdated and needs to be updated."
    echo "        ESPEAK_LANGUAGE_IDENTIFIER must be set to the espeak-ng language identifier for the language of your dataset"
    echo "        eg: ESPEAK_LANGUAGE_IDENTIFIER=en-us"
    echo
    echo "    PIPER_FILENAME_PREFIX must be set to the language code Piper uses to name language files"
    echo "        eg: PIPER_FILENAME_PREFIX=en_US"
    echo
    echo "    either add these values to your dataset.conf file manually, or run:"
    echo
    echo "        DATASETS/create_dataset.sh <dataset_folder>"
    echo
    echo "    to rebuild the datasets.conf file."
    echo 
    echo "Exiting"
    exit 1
fi

if [ -e "$SETTINGS_FILE" ]; then 
    source "$SETTINGS_FILE"
else
    echo "could not find $SETTINGS_FILE. Exiting."
    exit 1
fi

previously_preprocessed() {
    if [[ -d "$CACHE_DIR" && -f "$CONFIG_JSON" && -f "$DATASET_JSONL" ]]; then
        echo "TRUE"
    else
        echo "FALSE"
    fi
}

purge_training_folder(){
   rm -r $CACHE_DIR
   rm $CONFIG_JSON
   rm $DATASET_JSONL
}

error_handler() {
  echo "An error occurred in the script. Exiting."
  exit 1
}

export -f error_handler
trap 'error_handler' ERR SIGINT SIGTERM

function check_preprocessed_data() {
    if [[ "$(previously_preprocessed)" == "TRUE" ]]; then
        echo
        echo "        training_folder directory already contains a pre-processed dataset. Please choose an option:"
        echo
        echo "            [1] Skip preprocessing (recommended if resuming a previous training session)" 
        echo "            [2] Preprocess the dataset again  (important if you have changed pronunciation rules) "
        echo             
        echo -ne "            [1,2]? "
        read -r redo

        if [[ -z "$redo" || "$redo" == "1" ]]; then
            echo "Skipping preprocessing."
            exit 0
        elif [[ "$redo" == "2" ]]; then
            echo "Cleaning training_folder prior to preprocessing..."
            purge_training_folder
            return 0
        else
            echo "Invalid option. Please choose either 1 or 2."
            check_preprocessed_data
        fi
    else
        echo "training folder is clean, proceeding with preprocessing."
    fi
}

check_preprocessed_data
echo 
echo "" 
echo -e "       Auto-configured sampling rate: $SAMPLING_RATE"         
echo -e "    Calculated value for max-workers: $MAX_WORKERS"
echo
echo

echo "Configuring Piper for language: ${ESPEAK_LANGUAGE_IDENTIFIER}"
echo "Running piper_train.preprocess in docker container"
echo
echo

docker exec textymcspeechy-piper bash -c "
  cd /app/piper/src/python && \
  python3 -m piper_train.preprocess \
    --language ${ESPEAK_LANGUAGE_IDENTIFIER} \
    --input-dir \"/app/tts_dojo/${DOJO_NAME}/target_voice_dataset\" \
    --output-dir \"/app/tts_dojo/${DOJO_NAME}/training_folder\" \
    --dataset-format ljspeech \
    --single-speaker \
    --sample-rate ${SAMPLING_RATE} \
    --max-workers ${MAX_WORKERS}
"
result=$?
if [ $result -eq 0 ];then 
    echo
    echo
    echo "    Successfully preprocessed dataset."
    echo 
    echo "    Press <Enter> to continue"
    read
    echo
else
    echo  "piper_train.preprocess failed.  Press <Enter> to exit."
    read
    exit 1
fi
exit 0
