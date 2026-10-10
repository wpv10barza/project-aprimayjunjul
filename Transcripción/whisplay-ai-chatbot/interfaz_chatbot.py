import gradio as gr
import requests

def procesar_audio(ruta_audio):
    if not ruta_audio:
        return "Por favor, graba un audio."
    
    url_servidor = "http://127.0.0.1:8000/transcribe"
    
    try:
        # Enviar el audio de Gradio a tu servidor de FastAPI
        with open(ruta_audio, "rb") as f:
            archivos = {"file": ("audio.wav", f, "audio/wav")}
            respuesta = requests.post(url_servidor, files=archivos)
        
        if respuesta.status_code == 200:
            datos = respuesta.json()
            return datos.get("text", "El servidor no devolvió texto.")
        else:
            return f"Error del servidor: {respuesta.status_code}"
            
    except requests.exceptions.ConnectionError:
        return "❌ Error: No se pudo conectar. ¿Tu servidor_maestro.py está corriendo en otra ventana?"
    except Exception as e:
        return f"❌ Error inesperado: {str(e)}"

# Crear la interfaz web gráfica
app = gr.Interface(
    fn=procesar_audio,
    inputs=gr.Audio(type="filepath", sources=["microphone"], label="🎙️ Graba tu mensaje"),
    outputs=gr.Textbox(label="✨ Texto Corregido por Gemma"),
    title="🤖 Interfaz Web: Whisper + Gemma",
    description="Asegúrate de tener tu 'servidor_maestro.py' corriendo en otra ventana antes de grabar.",
    allow_flagging="never"
)

if __name__ == "__main__":
    app.launch(server_name="127.0.0.1", server_port=7860)
