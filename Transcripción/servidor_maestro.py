import os
import sys
import time
import tempfile
import subprocess
import uvicorn
from fastapi import FastAPI, UploadFile, File

# 1. VERIFICACIÓN DE FFMPEG (Crítico para Whisper)
try:
    subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
except FileNotFoundError:
    print("❌ ERROR CRÍTICO: 'ffmpeg' no está instalado o no está en el PATH de Windows.")
    print("👉 Descárgalo de: https://github.com/BtbN/FFmpeg-Builds/releases")
    sys.exit(1)

import whisper

app = FastAPI(title="Servidor Maestro: Whisper + Gemma")
modelo_whisper = None

EXE_GEMMA = r"D:\118102025\Documents\trabajos\bi\llama-cli.exe"
MODEL_FILE = r"D:\118102025\Documents\trabajos\bi\gemma-2-9b-it-q4_k_m.gguf"

@app.on_event("startup")
async def cargar_modelo():
    global modelo_whisper
    print("\n" + "="*50)
    print(" 🚀 INICIANDO SUPER-SERVIDOR (DEPURACIÓN ACTIVA)")
    print("="*50)
    print("[1/2] Cargando Whisper 'small' (Modo Seguro VRAM)...")
    try:
        # Usamos 'small' para evitar que la RTX 3050 colapse
        modelo_whisper = whisper.load_model("small")
        print("✅ Whisper cargado exitosamente.")
    except Exception as e:
        print(f"❌ ERROR AL CARGAR WHISPER: {e}")
        sys.exit(1)
        
    print(f"[2/2] Servidor listo. Abre http://127.0.0.1:8000 en tu navegador.")

@app.get("/")
def ruta_principal():
    # Esta ruta evita el error 404 en el navegador
    return {"Mensaje": "✅ Servidor Operativo", "Modelo": "Whisper Small + Gemma 9B"}

@app.post("/transcribe")
async def transcribir_y_corregir(file: UploadFile = File(...)):
    print(f"\n📥 [1] Audio recibido...")
    inicio = time.time()
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await file.read())
        ruta_audio = tmp.name

    print("⏳ [2] Transcribiendo en GPU...")
    try:
        resultado = modelo_whisper.transcribe(ruta_audio)
        texto_crudo = resultado["text"].strip()
        print(f"🎙️ Texto crudo: {texto_crudo}")
    except Exception as e:
        print(f"❌ Error en transcripción: {e}")
        return {"error": str(e)}
    finally:
        os.remove(ruta_audio)

    texto_corregido = texto_crudo

    if texto_crudo and os.path.exists(EXE_GEMMA):
        print("🧠 [3] Enviando a Gemma 2 (Esto puede tardar 15-30 seg)...")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as f_in:
            f_in.write(texto_crudo)
            ruta_in = f_in.name
            
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as f_sys:
            f_sys.write("Eres un editor. Corrige la ortografía y gramática del texto. Devuelve ÚNICAMENTE el texto corregido.")
            ruta_sys = f_sys.name

        comando_gemma = [
            EXE_GEMMA, "-m", MODEL_FILE, "-f", ruta_in, 
            "--system-prompt-file", ruta_sys, "--temp", "0.0", 
            "-c", "512", "-n", "256", "--no-display-prompt"
        ]

        try:
            proceso = subprocess.run(comando_gemma, capture_output=True, text=True, encoding="utf-8")
            if proceso.returncode == 0:
                texto_corregido = proceso.stdout.strip()
                print(f"✨ Gemma 2 corrigió: {texto_corregido}")
            else:
                print(f"⚠️ Error en Gemma: {proceso.stderr}")
        except Exception as e:
            print(f"❌ Error al ejecutar llama-cli: {e}")
        finally:
            os.remove(ruta_in)
            os.remove(ruta_sys)

    return {"text": texto_corregido if texto_corregido else texto_crudo}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
