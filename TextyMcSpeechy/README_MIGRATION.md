# TextyMcSpeechy — migración desde Google Drive

Periodo identificado en Google Drive: abril de 2026.

## Propósito

Proyecto de utilidades para preparar datasets de voz y entrenar modelos Piper de texto a voz (TTS). Incluye herramientas de conversión de audio, preparación de VCTK, creación de dojos de entrenamiento y ejecución mediante Docker.

## Tecnologías y herramientas encontradas

- Bash / shell scripts.
- Docker y Docker Compose.
- Piper TTS.
- ffmpeg, SoX y utilidades de audio.
- eSpeak NG para reglas de pronunciación.
- TensorBoard para seguimiento del entrenamiento.

## Estructura migrada

- `VCTK_dataset_tools/`: preparación y conversión de datasets VCTK.
- `batch_audio_tools/`: utilidades de frecuencia de muestreo.
- `tts_dojo/`: creación y operación del entorno de entrenamiento.
- Scripts raíz para levantar/detener el contenedor.

## Exclusiones deliberadas

No se versionan datasets de audio, voces generadas, checkpoints/modelos, `.git` ni otros artefactos pesados o generados. Esos elementos permanecen en Google Drive y por ello la carpeta original no debe eliminarse de Drive.

Este documento solo describe elementos comprobados en los archivos recuperados del proyecto; no añade funcionalidades no observadas.