import gradio as gr
import requests
import os

def procesar_audio(ruta_audio):
    if not ruta_audio: return "⚠️ Sube un archivo."
    url_servidor = "http://127.0.0.1:8000/transcribe"
    try:
        with open(ruta_audio, "rb") as f:
            archivos = {"file": (os.path.basename(ruta_audio), f, "audio/wav")}
            respuesta = requests.post(url_servidor, files=archivos)
        return respuesta.json().get("text", "Sin respuesta.") if respuesta.status_code == 200 else f"Error: {respuesta.status_code}"
    except Exception as e: return f"❌ Error: {str(e)}"

app = gr.Interface(
    fn=procesar_audio,
    inputs=gr.Audio(type="filepath", sources=["microphone", "upload"], label="🎙️ Sube MP3 o graba"),
    outputs=gr.Textbox(label="✨ Resultado"),
    title="🤖 Transcriptor Local Pro"
)

if __name__ == "__main__":
    # Cambiamos a 7861 para evitar el bloqueo
    app.launch(server_name="127.0.0.1", server_port=7861)
