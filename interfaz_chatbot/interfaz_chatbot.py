import gradio as gr
import requests
import os

def procesar_audio(ruta_audio):
    if not ruta_audio:
        return "⚠️ Por favor, sube un archivo o graba un audio primero."
    
    url_servidor = "http://127.0.0.1:8000/transcribe"
    
    # Mostrar en consola qué archivo se está procesando
    nombre_archivo = os.path.basename(ruta_audio)
    print(f"🚀 Enviando al servidor: {nombre_archivo}")
    
    try:
        with open(ruta_audio, "rb") as f:
            archivos = {"file": (nombre_archivo, f, "audio/wav")}
            respuesta = requests.post(url_servidor, files=archivos)
        
        if respuesta.status_code == 200:
            datos = respuesta.json()
            return datos.get("text", "El servidor no devolvió texto.")
        else:
            return f"❌ Error del servidor: {respuesta.status_code} - {respuesta.text}"
            
    except requests.exceptions.ConnectionError:
        return "❌ Error: No se pudo conectar. ¿Tu 'servidor_maestro.py' está corriendo en el puerto 8000?"
    except Exception as e:
        return f"❌ Error inesperado: {str(e)}"

# Interfaz mejorada con carga de archivos
app = gr.Interface(
    fn=procesar_audio,
    inputs=gr.Audio(
        type="filepath", 
        sources=["microphone", "upload"], # <--- Ahora permite ambos
        label="🎙️ Graba o arrastra un archivo de audio (MP3, WAV, etc.)"
    ),
    outputs=gr.Textbox(label="✨ Transcripción y Corrección de Gemma"),
    title="🤖 Transcriptor Maestro: Whisper + Gemma",
    description="Sube un archivo local o usa el micrófono. El audio se procesará en tu GPU RTX 3050.",
)

if __name__ == "__main__":
    # Iniciamos en el puerto 7860
    app.launch(server_name="127.0.0.1", server_port=7860)
