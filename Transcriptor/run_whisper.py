import os
import torch
import whisper

# Configuración de rutas fijas
AUDIO_PATH = r"D:\118102025\Music\Audio de WhatsApp 2025-11-21 a las 10.32.21_488bdc0f.waptt.opus"

def inicializar_y_transcribir():
    print("\n=======================================================")
    print("🚀 INICIANDO PIPELINE DE TRANSCRIPCIÓN SIMBIÓTICA")
    print("=======================================================")
    
    # 1. Validar la existencia física del archivo de WhatsApp
    if not os.path.exists(AUDIO_PATH):
        print(f"❌ ERROR: El archivo de audio no existe en: {AUDIO_PATH}")
        return

    print(f"✔ Audio detectado correctamente.")
    print(f"📦 Cargando PyTorch ({torch.__version__}) compartido...")
    
    try:
        # 2. Cargar el modelo Whisper (usa la caché central C:\Users\ASUS\.cache\whisper)
        print("🧠 Cargando modelo 'base' en la CPU...")
        model = whisper.load_model("base", device="cpu")
        
        # 3. Procesar la transcripción forzando el idioma español
        print("🎙 Transcribiendo contenedor de audio de WhatsApp...")
        resultado = model.transcribe(AUDIO_PATH, language="es")
        
        print("\n📝 --- TRANSCRIPCIÓN COMPLETADA ---")
        print(resultado["text"].strip())
        print("=======================================================\n")
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {str(e)}")
        print("💡 TIP DEVOPS: Los archivos .opus de WhatsApp requieren la herramienta FFmpeg instalada en Windows.")

if __name__ == "__main__":
    inicializar_y_transcribir()
